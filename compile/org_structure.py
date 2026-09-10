"""Compatibility projection of the Knowledge Hub registry.

Existing callers still speak in organizations and legacy ``tier`` values.
Canonical definitions live in ``knowledge_structure.json``; this module
projects them into the prior API during the compatibility window.
"""

try:
    from knowledge_structure import STRUCTURE
except ModuleNotFoundError:  # direct file-loader compatibility in repository tests
    import pathlib
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from knowledge_structure import STRUCTURE


ORG_ORDER = list(STRUCTURE.organization_keys)
ORG_LABEL = STRUCTURE.organization_labels
ORG_SECTIONS = {org: [] for org in ORG_ORDER}
SECTION_LABEL = {}
for _space in STRUCTURE.spaces:
    for _section in _space.sections:
        for _tier in _section.legacy_tiers:
            ORG_SECTIONS[_space.steward].append(_tier)
            SECTION_LABEL[_tier] = _section.legacy_label_for(_tier)

TIER_ORDER = list(ORG_SECTIONS["transpara-ai"])
TIER_LABEL = {tier: SECTION_LABEL[tier] for tier in TIER_ORDER}
DEFAULT_ORG = "transpara-ai"

# which repo-nav groups render under which org band (intake decision 2)
ORG_REPO_GROUPS = {
    "transpara": ["platform"],
    "transpara-ai": ["civilization", "other"],
}


def resolve_org_tier(slug, org_present, org_value, tier_value):
    """Fail-closed org/tier resolution for one article (DP D3).

    Allowlist, never denylist: the ONLY accepted states are (a) no org key at
    all -> DEFAULT_ORG, or (b) an org value exactly in ORG_ORDER; and in both
    cases a tier exactly in ORG_SECTIONS[org]. Everything else — empty org,
    unknown org, missing tier, tier foreign to the org — raises ValueError
    naming the slug, the value, and the allowlist. There is no tier default.
    """
    if org_present:
        if org_value not in ORG_ORDER:
            raise ValueError(
                "%s: org %r is not in the allowlist %s"
                % (slug, org_value, ORG_ORDER))
        org = org_value
    else:
        org = DEFAULT_ORG
    if tier_value not in ORG_SECTIONS[org]:
        raise ValueError(
            "%s: tier %r is not valid for org %r (allowlist: %s)"
            % (slug, tier_value, org, ORG_SECTIONS[org]))
    return org, tier_value
