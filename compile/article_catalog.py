#!/usr/bin/env python3
"""Canonical article discovery and multi-space metadata validation."""

from dataclasses import dataclass
import pathlib
import re

from knowledge_structure import STRUCTURE, KnowledgeStructure, StructureError


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_ORG = "transpara-ai"


class CatalogError(ValueError):
    """An article cannot be admitted to the canonical catalog."""


def split_frontmatter(raw):
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            return raw[3:end].strip("\n"), raw[end + 4:].lstrip("\n")
    return "", raw


def has_key(frontmatter, key):
    return bool(re.search(r"(?m)^%s\s*:" % re.escape(key), frontmatter))


def _strip_inline_comment(value):
    quote = ""
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if char == "\\" and quote:
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = ""
            continue
        if char in "\"'":
            quote = char
        elif char == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.strip()


def scalar(frontmatter, key):
    match = re.search(r"(?m)^%s:[ \t]*(.*)$" % re.escape(key), frontmatter)
    if not match:
        return ""
    value = _strip_inline_comment(match.group(1)).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value.strip()


def list_values(frontmatter, key):
    lines = frontmatter.splitlines()
    key_index = None
    inline = ""
    for index, line in enumerate(lines):
        match = re.match(r"^%s:[ \t]*(.*)$" % re.escape(key), line)
        if match:
            if key_index is not None:
                raise CatalogError("frontmatter key %r appears more than once" % key)
            key_index = index
            inline = _strip_inline_comment(match.group(1)).strip()
    if key_index is None:
        return []
    if inline:
        if not (inline.startswith("[") and inline.endswith("]")):
            return [inline.strip().strip("\"").strip("'")]
        body = inline[1:-1].strip()
        if not body:
            return []
        return [part.strip().strip("\"").strip("'")
                for part in body.split(",") if part.strip()]
    values = []
    for line in lines[key_index + 1:]:
        if re.match(r"^[A-Za-z0-9_-]+\s*:", line):
            break
        match = re.match(r"^[ \t]+-[ \t]+(.*)$", line)
        if match:
            value = _strip_inline_comment(match.group(1)).strip().strip("\"").strip("'")
            if value:
                values.append(value)
        elif line.strip() and not line.startswith((" ", "\t")):
            break
    return values


@dataclass(frozen=True)
class ArticleRecord:
    slug: str
    path: pathlib.Path
    title: str
    org: str
    tier: str
    primary_placement: str
    placements: tuple[str, ...]
    classification: str
    source_authorities: tuple[str, ...]
    retired_on: str
    sources: tuple[str, ...]
    raw_documents: tuple[str, ...]
    frontmatter: str
    body: str
    compatibility_fields: tuple[str, ...]

    @property
    def primary_space(self):
        return self.primary_placement.split("/", 1)[0]

    @property
    def primary_section(self):
        return self.primary_placement.split("/", 1)[1]

    def is_in_space(self, space):
        prefix = space + "/"
        return any(placement.startswith(prefix) for placement in self.placements)

    def section_in_space(self, space):
        prefix = space + "/"
        for placement in self.placements:
            if placement.startswith(prefix):
                return placement.split("/", 1)[1]
        return ""


class ArticleCatalog:
    def __init__(self, records, structure=STRUCTURE):
        self.records = tuple(records)
        self.structure = structure
        self.by_slug = {record.slug: record for record in self.records}
        if len(self.by_slug) != len(self.records):
            raise CatalogError("canonical article slugs must be unique")

    def __iter__(self):
        return iter(self.records)

    def __len__(self):
        return len(self.records)

    def for_space(self, space, *, include_retired=False):
        if space not in self.structure.space_map:
            raise CatalogError("unknown space %r" % space)
        return tuple(record for record in self.records
                     if record.is_in_space(space)
                     and (include_retired or not record.retired_on))

    def counts(self):
        return {
            "article_count": len(self.records),
            "space_counts": {
                space.key: len(self.for_space(space.key, include_retired=True))
                for space in self.structure.spaces
            },
        }


def _record(path, structure, *, compatibility, require_explicit):
    frontmatter, body = split_frontmatter(path.read_text())
    slug = path.stem
    title = scalar(frontmatter, "entity") or slug.replace("-", " ")
    tier = scalar(frontmatter, "tier")
    compatibility_fields = []

    if has_key(frontmatter, "org"):
        org = scalar(frontmatter, "org")
    elif compatibility:
        org = DEFAULT_ORG
        compatibility_fields.append("org")
    else:
        org = ""
    if org not in structure.organization_keys:
        raise CatalogError(
            "%s: org %r is not in the allowlist %s"
            % (slug, org, list(structure.organization_keys)))

    if has_key(frontmatter, "primary_placement"):
        primary = scalar(frontmatter, "primary_placement")
    elif compatibility:
        try:
            primary = structure.legacy_placement(org, tier)
        except StructureError as exc:
            raise CatalogError("%s: %s" % (slug, exc)) from exc
        compatibility_fields.append("primary_placement")
    else:
        primary = ""

    if has_key(frontmatter, "placements"):
        placements = list_values(frontmatter, "placements")
    elif compatibility:
        placements = [primary]
        compatibility_fields.append("placements")
    else:
        placements = []

    if has_key(frontmatter, "classification"):
        classification = scalar(frontmatter, "classification")
    elif compatibility:
        classification = "internal"
        compatibility_fields.append("classification")
    else:
        classification = ""

    if require_explicit and compatibility_fields:
        raise CatalogError(
            "%s: missing explicit fields: %s"
            % (slug, ", ".join(compatibility_fields)))
    try:
        primary_space, _ = structure.split_placement(primary)
        for placement in placements:
            structure.split_placement(placement)
    except StructureError as exc:
        raise CatalogError("%s: %s" % (slug, exc)) from exc
    if len(placements) != len(set(placements)):
        raise CatalogError("%s: placements must be unique" % slug)
    if primary not in placements:
        raise CatalogError("%s: primary_placement must be present in placements" % slug)
    if structure.space_map[primary_space].steward != org:
        raise CatalogError(
            "%s: org %r does not steward primary space %r"
            % (slug, org, primary_space))
    if classification not in structure.classification_keys:
        raise CatalogError(
            "%s: classification %r is not in the allowlist %s"
            % (slug, classification, list(structure.classification_keys)))

    source_authorities = list_values(frontmatter, "source_authority")
    if not source_authorities:
        authority_scalar = scalar(frontmatter, "source_authority")
        source_authorities = [authority_scalar] if authority_scalar else []
    unknown_authorities = sorted(set(source_authorities) - set(structure.source_authorities))
    if unknown_authorities:
        raise CatalogError(
            "%s: unknown source_authority values %s"
            % (slug, unknown_authorities))

    return ArticleRecord(
        slug=slug,
        path=path,
        title=title,
        org=org,
        tier=tier,
        primary_placement=primary,
        placements=tuple(placements),
        classification=classification,
        source_authorities=tuple(source_authorities),
        retired_on=scalar(frontmatter, "retired_on"),
        sources=tuple(list_values(frontmatter, "sources")),
        raw_documents=tuple(list_values(frontmatter, "raw_documents")),
        frontmatter=frontmatter,
        body=body,
        compatibility_fields=tuple(compatibility_fields),
    )


def load_catalog(root=ROOT, *, structure=STRUCTURE, compatibility=True,
                 require_explicit=False, wiki_dir=None):
    root = pathlib.Path(root)
    wiki = pathlib.Path(wiki_dir) if wiki_dir is not None else root / "wiki"
    try:
        paths = sorted(wiki.glob("*.md"))
    except OSError as exc:
        raise CatalogError("cannot discover articles under %s: %s" % (wiki, exc)) from exc
    records = []
    for path in paths:
        try:
            records.append(_record(
                path, structure,
                compatibility=compatibility,
                require_explicit=require_explicit,
            ))
        except OSError as exc:
            raise CatalogError("cannot read article %s: %s" % (path, exc)) from exc
    return ArticleCatalog(records, structure=structure)


CATALOG = load_catalog()
