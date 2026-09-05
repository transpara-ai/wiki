#!/usr/bin/env python3
"""Governance gates for the curated Platform and Competition seed sets."""
from datetime import date
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from article_catalog import load_catalog, scalar  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parents[1]

PLATFORM_SEEDS = {
    "transpara-product-portfolio",
    "transpara-platform-overview",
    "transpara-rtoi",
    "transpara-platform-architecture",
    "transpara-platform-components",
    "visual-kpi",
    "transpara-data-ingestion-vdl",
    "transpara-deployment-air-gap",
    "transpara-security-compliance",
    "platform-transpara-mcp-boundary",
    "transpara-operations-troubleshooting",
    "transpara-decisions-reference",
}

COMPETITION_SEEDS = {
    "competition-overview",
    "competition-competitor-index",
    "competitor-cognite-data-fusion",
    "competitor-aveva-pi-system",
    "competitor-seeq",
    "competition-rtoi-comparison",
    "competition-ai-sdr-market",
    "competitor-11x",
    "competitor-artisan",
    "competition-positioning-objections",
    "competition-win-loss-template",
    "competition-research-method",
}

TIME_SENSITIVE_COMPETITION = COMPETITION_SEEDS - {
    "competition-win-loss-template", "competition-research-method",
    "competition-positioning-objections"}

POSITIONING_SEEDS = {
    "competition-overview",
    "competitor-cognite-data-fusion",
    "competitor-aveva-pi-system",
    "competitor-seeq",
    "competition-rtoi-comparison",
    "competitor-11x",
    "competitor-artisan",
    "competition-positioning-objections",
}


def iso(frontmatter, key):
    value = scalar(frontmatter, key)
    assert value, "missing %s" % key
    return date.fromisoformat(value)


def test_seed_inventory_and_common_governance():
    catalog = load_catalog(ROOT, require_explicit=True).by_slug
    expected = PLATFORM_SEEDS | COMPETITION_SEEDS
    assert expected.issubset(catalog), sorted(expected - set(catalog))
    actual = {slug for slug, record in catalog.items()
              if record.classification == "company-internal"}
    assert actual == expected, "reviewed seed inventory drifted: %s" % sorted(actual ^ expected)
    for slug in expected:
        record = catalog[slug]
        assert record.org == "transpara"
        assert record.classification == "company-internal"
        assert record.sources, "%s has no current sources" % slug
        assert record.source_authorities, "%s has no source authority" % slug
        assert iso(record.frontmatter, "reviewed_on")
        assert iso(record.frontmatter, "review_by") >= iso(record.frontmatter, "reviewed_on")
    print("ok test_seed_inventory_and_common_governance")


def test_platform_seeds_have_authoritative_platform_sources():
    catalog = load_catalog(ROOT).by_slug
    for slug in PLATFORM_SEEDS:
        record = catalog[slug]
        assert record.primary_placement.startswith("platform/")
        assert any(
            source.startswith("/Transpara/transpara-ai/repos/platform/")
            or source.startswith("https://www.transpara.com/")
            for source in record.sources
        ), "%s lacks an authoritative Platform source" % slug
        assert any(authority in record.source_authorities for authority in {
            "code", "configuration", "adr", "engineering-docs", "public-docs"})
    print("ok test_platform_seeds_have_authoritative_platform_sources")


def test_time_sensitive_competition_claims_are_bounded():
    catalog = load_catalog(ROOT).by_slug
    for slug in TIME_SENSITIVE_COMPETITION:
        record = catalog[slug]
        verified = iso(record.frontmatter, "verified_at")
        review_by = iso(record.frontmatter, "review_by")
        assert 0 <= (review_by - verified).days <= 92, slug
        assert "external-primary-source" in record.source_authorities, slug
        assert any(source.startswith("https://") for source in record.sources), slug
    for slug in POSITIONING_SEEDS:
        record = catalog[slug]
        assert "first-party positioning" in record.body.lower(), slug
    print("ok test_time_sensitive_competition_claims_are_bounded")


def test_sensitive_and_agent_boundaries_are_explicit():
    catalog = load_catalog(ROOT).by_slug
    ai_sdr_refs = [
        record for record in catalog.values()
        if any("/repos/ai-sdr/" in source for source in record.sources)
    ]
    assert [record.slug for record in ai_sdr_refs] == ["competition-ai-sdr-market"]
    body = ai_sdr_refs[0].body.lower()
    assert "not an authority for external competitor facts" in body
    win_loss = catalog["competition-win-loss-template"].body.lower()
    for boundary in ("do not put customer names", "personal data", "authorized source system"):
        assert boundary in win_loss
    method = catalog["competition-research-method"].body.lower()
    assert "do not auto-export ai-sdr investigations" in method
    assert "human publication approval" in method
    print("ok test_sensitive_and_agent_boundaries_are_explicit")


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print("\nall %d seed-content tests passed" % len(tests))
