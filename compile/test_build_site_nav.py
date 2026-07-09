#!/usr/bin/env python3
"""Stdlib-assert tests for generated sidebar navigation invariants."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_site as site  # noqa: E402


def investigation_articles_by_topic():
    grouped = {}
    for article in site.META.values():
        if article["tier"] != "investigation":
            continue
        topic = site.investigation_topic_for(article["slug"], article)
        if topic:
            grouped.setdefault(topic, []).append(article)
    return grouped


def test_single_article_topic_counts_match_flat_article_counts():
    grouped = investigation_articles_by_topic()
    singleton_topics = {
        topic: articles[0]
        for topic, articles in grouped.items()
        if len(articles) == 1
    }
    if not singleton_topics:
        print("skip test_single_article_topic_counts_match_flat_article_counts: no single-article topic fixtures")
        return

    for topic, article in singleton_topics.items():
        aggregate_count = site.raw_doc_count_for_articles([article])
        flat_count = len(site.raw_doc_refs(site.article_frontmatter(article["slug"])))
        assert aggregate_count == flat_count, (
            "%s direct-row count %d disagrees with flat article count %d"
            % (topic, aggregate_count, flat_count)
        )

    print("ok test_single_article_topic_counts_match_flat_article_counts")


def test_direct_contribution_marker_uses_only_contributed_values():
    old_frontmatter = site.article_frontmatter
    values = {
        "direct": 'civilization_contribution: "Contributed the governed recall-adapter pattern."\n',
        "future": 'civilization_contribution: "slated as potential future usage."\n',
        "reference": 'civilization_contribution: "Not directly included, but used as reference."\n',
        "missing": "",
    }
    try:
        site.article_frontmatter = lambda slug: values.get(slug, "")
        assert site.article_direct_contribution({"slug": "direct"}) == "Contributed the governed recall-adapter pattern."
        assert site.article_direct_contribution({"slug": "future"}) == ""
        assert site.article_direct_contribution({"slug": "reference"}) == ""
        assert site.article_direct_contribution({"slug": "missing"}) == ""
    finally:
        site.article_frontmatter = old_frontmatter
    print("ok test_direct_contribution_marker_uses_only_contributed_values")


def test_single_article_topics_render_as_direct_rows_and_multi_topics_stay_grouped():
    articles = [
        {"slug": "single-topic", "title": "Single Topic Article", "tier": "investigation"},
        {"slug": "multi-topic-a", "title": "Multi Topic A", "tier": "investigation"},
        {"slug": "multi-topic-b", "title": "Multi Topic B", "tier": "investigation"},
    ]
    topics = {
        "single-topic": "Single Topic",
        "multi-topic-a": "Multi Topic",
        "multi-topic-b": "Multi Topic",
    }
    old_topic = site.investigation_topic_for
    old_count = site.raw_doc_count_for_articles
    old_contribution = site.article_direct_contribution
    try:
        site.investigation_topic_for = lambda slug, meta: topics.get(slug, "")
        site.raw_doc_count_for_articles = lambda grouped_articles: len(grouped_articles)
        site.article_direct_contribution = lambda article: (
            "Contributed a direct Civilization pattern."
            if article["slug"] in {"single-topic", "multi-topic-a"} else ""
        )
        nav = site.build_investigation_nav(articles, "single-topic")
    finally:
        site.investigation_topic_for = old_topic
        site.raw_doc_count_for_articles = old_count
        site.article_direct_contribution = old_contribution

    single_row = (
        '<li class="nav-article-row"><a class="current" href="single-topic.html" '
        'title="Single Topic Article">Single Topic</a>'
        '<span class="nav-contribution-marker" title="Civilization contribution: c — '
        'Contributed a direct Civilization pattern." '
        'aria-label="Civilization contribution marker: c">c</span><em>1</em></li>'
    )
    assert single_row in nav
    assert '<summary><span>Single Topic</span>' not in nav
    assert '<details class="nav-subgroup"' in nav
    assert (
        '<summary><span>Multi Topic</span><span class="nav-contribution-marker" '
        'title="Civilization contribution: c — Contributed a direct Civilization pattern." '
        'aria-label="Civilization contribution marker: c">c</span><em>2</em></summary>'
    ) in nav
    assert 'href="multi-topic-a.html">Multi Topic A</a>' in nav
    assert 'href="multi-topic-b.html">Multi Topic B</a>' in nav
    print("ok test_single_article_topics_render_as_direct_rows_and_multi_topics_stay_grouped")


# ---- R9 / AC10 — single nav entry per investigation (investigation_primary) ----

def _r9_articles():
    return [
        {"slug": "eval", "title": "Sakana Eval", "tier": "investigation"},
        {"slug": "adjacent", "title": "Sakana Adjacent", "tier": "investigation"},
        {"slug": "solo", "title": "Solo Topic", "tier": "investigation"},
    ]


def _with_r9(topics, primaries, fn):
    old = (site.investigation_topic_for, site.investigation_primary_flag,
           site.raw_doc_count_for_articles, site.nav_contribution_marker)
    try:
        site.investigation_topic_for = lambda slug, meta=None: topics.get(slug, "")
        site.investigation_primary_flag = lambda slug: slug in primaries
        site.raw_doc_count_for_articles = lambda arts: len(arts)
        site.nav_contribution_marker = lambda arts: ""
        return fn()
    finally:
        (site.investigation_topic_for, site.investigation_primary_flag,
         site.raw_doc_count_for_articles, site.nav_contribution_marker) = old


def test_multipage_cluster_with_primary_renders_single_row():
    topics = {"eval": "Sakana AI", "adjacent": "Sakana AI", "solo": "Solo"}
    nav = _with_r9(topics, {"eval"}, lambda: site.build_investigation_nav(_r9_articles(), "eval"))
    assert 'href="eval.html"' in nav and '>Sakana AI</a>' in nav, "primary row labeled by topic"
    assert 'href="adjacent.html"' not in nav, "companion omitted from the nav"
    assert '<details class="nav-subgroup"' not in nav, "collapsed to a flat row, not a group"
    print("ok test_multipage_cluster_with_primary_renders_single_row")


def test_cluster_without_primary_falls_back_to_group():
    topics = {"eval": "Sakana AI", "adjacent": "Sakana AI", "solo": "Solo"}
    nav = _with_r9(topics, set(), lambda: site.build_investigation_nav(_r9_articles(), "eval"))
    assert '<details class="nav-subgroup"' in nav, "0 primaries -> fail-safe expandable group"
    assert 'href="eval.html"' in nav and 'href="adjacent.html"' in nav, "both members shown"
    print("ok test_cluster_without_primary_falls_back_to_group")


def test_multiple_primaries_flagged_and_group_rendered():
    topics = {"eval": "Sakana AI", "adjacent": "Sakana AI", "solo": "Solo"}
    def run():
        cluster = [a for a in _r9_articles() if topics[a["slug"]] == "Sakana AI"]
        assert site.cluster_representative(cluster) is None, ">=2 primaries -> no representative"
        return site.build_investigation_nav(_r9_articles(), "eval")
    nav = _with_r9(topics, {"eval", "adjacent"}, run)
    assert '<details class="nav-subgroup"' in nav, "render falls back to the full group"
    assert 'href="eval.html"' in nav and 'href="adjacent.html"' in nav
    print("ok test_multiple_primaries_flagged_and_group_rendered")


def test_retired_primary_falls_back_and_is_flagged():
    # a retired primary is absent from the active `arts`; the active members have
    # no primary -> no representative -> fail-safe group (the corpus check flags it).
    topics = {"eval": "Sakana AI", "adjacent": "Sakana AI"}
    active = [{"slug": "eval", "title": "Sakana Eval", "tier": "investigation"},
              {"slug": "adjacent", "title": "Sakana Adjacent", "tier": "investigation"}]
    def run():
        assert site.cluster_representative(active) is None, "no active primary -> no representative"
        return site.build_investigation_nav(active, "eval")
    nav = _with_r9(topics, {"retired-primary"}, run)  # designated primary is retired/absent
    assert '<details class="nav-subgroup"' in nav
    assert 'href="eval.html"' in nav and 'href="adjacent.html"' in nav
    print("ok test_retired_primary_falls_back_and_is_flagged")


def test_stray_primary_on_single_page_is_inert():
    # investigation_primary on a single-page topic has no effect: still one flat
    # row (the single-article path); the collapse requires >=2 members.
    topics = {"solo": "Solo"}
    arts = [{"slug": "solo", "title": "Solo Topic", "tier": "investigation"}]
    nav = _with_r9(topics, {"solo"}, lambda: site.build_investigation_nav(arts, "solo"))
    assert 'href="solo.html"' in nav
    assert '<details class="nav-subgroup"' not in nav
    print("ok test_stray_primary_on_single_page_is_inert")


def test_navbox_investigation_row_collapses_by_primary():
    topics = {"eval": "Sakana AI", "adjacent": "Sakana AI", "solo": "Solo"}
    reps = _with_r9(topics, {"eval"}, lambda: site.navbox_investigation_reps(_r9_articles()))
    slugs = [a["slug"] for a in reps]
    assert "eval" in slugs and "solo" in slugs, "primary + single-page topic kept"
    assert "adjacent" not in slugs, "non-primary companion collapsed out of the navbox"
    print("ok test_navbox_investigation_row_collapses_by_primary")


def test_collapsed_cluster_row_is_current_for_any_member():
    # CFAR (Codex): the collapsed cluster row (one primary) represents the WHOLE
    # cluster, so it is marked `current` when viewing ANY member — including a
    # non-primary companion — not only the primary.
    topics = {"eval": "Sakana AI", "adjacent": "Sakana AI", "solo": "Solo"}

    def _row(nav, href):
        for seg in nav.split("<li")[1:]:
            body = seg.split("</li>", 1)[0]
            if href in body:
                return body
        return ""

    # viewing the NON-primary companion → the single primary row is current
    nav = _with_r9(topics, {"eval"}, lambda: site.build_investigation_nav(_r9_articles(), "adjacent"))
    assert 'class="current"' in _row(nav, 'href="eval.html"'), \
        "collapsed row is current when viewing a non-primary member"
    # viewing the primary itself is still current (unchanged)
    nav2 = _with_r9(topics, {"eval"}, lambda: site.build_investigation_nav(_r9_articles(), "eval"))
    assert 'class="current"' in _row(nav2, 'href="eval.html"')
    # a different cluster's current state does not bleed onto this row
    nav3 = _with_r9(topics, {"eval"}, lambda: site.build_investigation_nav(_r9_articles(), "solo"))
    assert 'class="current"' not in _row(nav3, 'href="eval.html"'), \
        "the cluster row is not current when an unrelated article is current"
    print("ok test_collapsed_cluster_row_is_current_for_any_member")


def test_investigation_primary_strict_boolean():
    cases = {
        "t1": "investigation_primary: true\n",
        "t2": 'investigation_primary: "true"\n',
        "f1": "investigation_primary: false\n",
        "f2": 'investigation_primary: "false"\n',
        "f3": "investigation_primary: yes\n",
        "f4": "investigation_primary: 1\n",
        "f5": "investigation_primary:\n",
        "f6": "entity: x\n",
    }
    old = site.article_frontmatter
    try:
        site.article_frontmatter = lambda slug: cases.get(slug, "")
        assert site.investigation_primary_flag("t1") is True
        assert site.investigation_primary_flag("t2") is True
        for s in ("f1", "f2", "f3", "f4", "f5", "f6"):
            assert site.investigation_primary_flag(s) is False, "%s must NOT be primary" % s
    finally:
        site.article_frontmatter = old
    print("ok test_investigation_primary_strict_boolean")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d build-site nav tests passed" % len(fns))
