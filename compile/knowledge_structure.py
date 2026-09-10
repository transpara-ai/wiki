#!/usr/bin/env python3
"""Validated information architecture for the Transpara Knowledge Hub.

The JSON registry is the single source for organizations, spaces, sections,
classifications, source-authority vocabulary, and publication profiles.  This
module is deliberately side-effect free beyond reading that committed file so
builders, lifecycle tools, and tests share one fail-closed interpretation.
"""

from dataclasses import dataclass
import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = ROOT / "compile" / "knowledge_structure.json"


class StructureError(ValueError):
    """The committed knowledge structure is malformed or ambiguous."""


@dataclass(frozen=True)
class Section:
    key: str
    label: str
    legacy_labels: tuple[tuple[str, str], ...]
    legacy_tiers: tuple[str, ...]

    def legacy_label_for(self, tier):
        return dict(self.legacy_labels).get(tier, self.label)


@dataclass(frozen=True)
class Space:
    key: str
    label: str
    steward: str
    description: str
    sections: tuple[Section, ...]

    @property
    def section_keys(self):
        return tuple(section.key for section in self.sections)


@dataclass(frozen=True)
class PublicationProfile:
    key: str
    enabled: bool
    classifications: tuple[str, ...]
    spaces: tuple[str, ...]
    include_sources: bool
    include_repositories: bool
    include_ingest: bool


@dataclass(frozen=True)
class KnowledgeStructure:
    schema_version: int
    site_name: str
    default_space: str
    organizations: tuple[tuple[str, str], ...]
    classifications: tuple[tuple[str, str], ...]
    source_authorities: tuple[str, ...]
    spaces: tuple[Space, ...]
    publication_profiles: tuple[PublicationProfile, ...]

    @property
    def organization_keys(self):
        return tuple(key for key, _ in self.organizations)

    @property
    def organization_labels(self):
        return dict(self.organizations)

    @property
    def classification_keys(self):
        return tuple(key for key, _ in self.classifications)

    @property
    def classification_labels(self):
        return dict(self.classifications)

    @property
    def space_map(self):
        return {space.key: space for space in self.spaces}

    @property
    def profile_map(self):
        return {profile.key: profile for profile in self.publication_profiles}

    def split_placement(self, placement):
        if not isinstance(placement, str) or placement.count("/") != 1:
            raise StructureError("placement %r must be '<space>/<section>'" % placement)
        space_key, section_key = placement.split("/", 1)
        space = self.space_map.get(space_key)
        if not space:
            raise StructureError(
                "placement %r names unknown space (allowlist: %s)"
                % (placement, list(self.space_map)))
        if section_key not in space.section_keys:
            raise StructureError(
                "placement %r names unknown section (allowlist: %s)"
                % (placement, list(space.section_keys)))
        return space_key, section_key

    def section(self, placement):
        space_key, section_key = self.split_placement(placement)
        return next(section for section in self.space_map[space_key].sections
                    if section.key == section_key)

    def legacy_placement(self, org, tier):
        matches = []
        for space in self.spaces:
            if space.steward != org:
                continue
            for section in space.sections:
                if tier in section.legacy_tiers:
                    matches.append("%s/%s" % (space.key, section.key))
        if len(matches) != 1:
            raise StructureError(
                "legacy org/tier %r/%r resolves to %d placements; expected exactly one"
                % (org, tier, len(matches)))
        return matches[0]

    def profile(self, key, *, require_enabled=True):
        profile = self.profile_map.get(key)
        if not profile:
            raise StructureError(
                "unknown publication profile %r (allowlist: %s)"
                % (key, list(self.profile_map)))
        if require_enabled and not profile.enabled:
            raise StructureError("publication profile %r is disabled" % key)
        return profile


def _required_string(value, where):
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise StructureError("%s must be a non-empty trimmed string" % where)
    return value


def _unique_records(records, where):
    if not isinstance(records, list) or not records:
        raise StructureError("%s must be a non-empty list" % where)
    seen = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise StructureError("%s[%d] must be an object" % (where, index))
        key = _required_string(record.get("key"), "%s[%d].key" % (where, index))
        if key in seen:
            raise StructureError("%s contains duplicate key %r" % (where, key))
        seen.add(key)
    return records


def _bool(record, key, where):
    value = record.get(key)
    if type(value) is not bool:
        raise StructureError("%s.%s must be boolean" % (where, key))
    return value


def load_structure(path=DEFAULT_REGISTRY_PATH):
    path = pathlib.Path(path)
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise StructureError("cannot load knowledge structure %s: %s" % (path, exc)) from exc
    if not isinstance(payload, dict):
        raise StructureError("knowledge structure root must be an object")
    if payload.get("schema_version") != 1:
        raise StructureError("knowledge structure schema_version must be 1")
    site_name = _required_string(payload.get("site_name"), "site_name")

    org_records = _unique_records(payload.get("organizations"), "organizations")
    organizations = tuple(
        (record["key"], _required_string(record.get("label"), "organization label"))
        for record in org_records)
    org_keys = {key for key, _ in organizations}

    classification_records = _unique_records(
        payload.get("classifications"), "classifications")
    classifications = tuple(
        (record["key"], _required_string(record.get("label"), "classification label"))
        for record in classification_records)
    classification_keys = {key for key, _ in classifications}

    source_authorities = payload.get("source_authorities")
    if (not isinstance(source_authorities, list) or not source_authorities
            or any(not isinstance(value, str) or not value for value in source_authorities)
            or len(source_authorities) != len(set(source_authorities))):
        raise StructureError("source_authorities must be a non-empty unique string list")

    spaces = []
    for index, record in enumerate(_unique_records(payload.get("spaces"), "spaces")):
        where = "spaces[%d]" % index
        steward = _required_string(record.get("steward"), "%s.steward" % where)
        if steward not in org_keys:
            raise StructureError("%s.steward %r is not an organization" % (where, steward))
        sections = []
        for section_index, section_record in enumerate(
                _unique_records(record.get("sections"), "%s.sections" % where)):
            section_where = "%s.sections[%d]" % (where, section_index)
            legacy_tiers = section_record.get("legacy_tiers", [])
            if (not isinstance(legacy_tiers, list)
                    or any(not isinstance(value, str) or not value for value in legacy_tiers)
                    or len(legacy_tiers) != len(set(legacy_tiers))):
                raise StructureError("%s.legacy_tiers must be a unique string list" % section_where)
            legacy_labels = section_record.get("legacy_labels")
            if legacy_labels is None:
                label = _required_string(
                    section_record.get("legacy_label", section_record.get("label")),
                    "%s.legacy_label" % section_where,
                )
                legacy_labels = {tier: label for tier in legacy_tiers}
            if (not isinstance(legacy_labels, dict)
                    or set(legacy_labels) != set(legacy_tiers)
                    or any(not isinstance(value, str) or not value
                           for value in legacy_labels.values())):
                raise StructureError(
                    "%s.legacy_labels must label every legacy tier exactly once"
                    % section_where)
            sections.append(Section(
                key=section_record["key"],
                label=_required_string(section_record.get("label"), "%s.label" % section_where),
                legacy_labels=tuple((tier, legacy_labels[tier]) for tier in legacy_tiers),
                legacy_tiers=tuple(legacy_tiers),
            ))
        spaces.append(Space(
            key=record["key"],
            label=_required_string(record.get("label"), "%s.label" % where),
            steward=steward,
            description=_required_string(record.get("description"), "%s.description" % where),
            sections=tuple(sections),
        ))
    space_keys = {space.key for space in spaces}
    default_space = _required_string(payload.get("default_space"), "default_space")
    if default_space not in space_keys:
        raise StructureError("default_space %r is not registered" % default_space)

    profiles = []
    for index, record in enumerate(_unique_records(
            payload.get("publication_profiles"), "publication_profiles")):
        where = "publication_profiles[%d]" % index
        allowed = record.get("classifications")
        if (not isinstance(allowed, list) or not allowed
                or any(value not in classification_keys for value in allowed)
                or len(allowed) != len(set(allowed))):
            raise StructureError("%s.classifications must be a unique classification allowlist" % where)
        profile_spaces = record.get("spaces", list(space_keys))
        if (not isinstance(profile_spaces, list)
                or any(value not in space_keys for value in profile_spaces)
                or len(profile_spaces) != len(set(profile_spaces))):
            raise StructureError("%s.spaces must be a unique space allowlist" % where)
        profiles.append(PublicationProfile(
            key=record["key"],
            enabled=_bool(record, "enabled", where),
            classifications=tuple(allowed),
            spaces=tuple(profile_spaces),
            include_sources=_bool(record, "include_sources", where),
            include_repositories=_bool(record, "include_repositories", where),
            include_ingest=_bool(record, "include_ingest", where),
        ))

    return KnowledgeStructure(
        schema_version=1,
        site_name=site_name,
        default_space=default_space,
        organizations=organizations,
        classifications=classifications,
        source_authorities=tuple(source_authorities),
        spaces=tuple(spaces),
        publication_profiles=tuple(profiles),
    )


STRUCTURE = load_structure()
