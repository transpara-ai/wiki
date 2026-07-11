"""Single source for the wiki's org/section information architecture.

Pure data + one pure resolver — deliberately side-effect-free (no I/O, no
META build, no edge state) so both the builder (build_site.py) and the ingest
server (ingest_server.py) can import it safely (DP-20260710-wiki-org-sections
D1/B4). Sections remain the article `tier:` frontmatter mechanism; an org
simply scopes which tier values are legal.
"""

TIER_ORDER = ["foundational", "institutional", "architecture", "arc",
              "investigation", "concept", "meta"]
TIER_LABEL = {
    "foundational": "Foundational — source philosophy",
    "institutional": "Institutional substrate",
    "architecture": "Architecture",
    "arc": "The dark-factory arc",
    "investigation": "Investigations",
    "concept": "Concepts",
    "meta": "Meta",
}

ORG_ORDER = ["transpara", "transpara-ai"]
ORG_LABEL = {"transpara": "Transpara", "transpara-ai": "Transpara-AI"}
ORG_SECTIONS = {
    "transpara": ["organization", "product"],
    "transpara-ai": list(TIER_ORDER),
}
SECTION_LABEL = dict(TIER_LABEL, **{
    "organization": "Organization",
    "product": "Product",
})
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
