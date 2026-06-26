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
    try:
        site.investigation_topic_for = lambda slug, meta: topics.get(slug, "")
        site.raw_doc_count_for_articles = lambda grouped_articles: len(grouped_articles)
        nav = site.build_investigation_nav(articles, "single-topic")
    finally:
        site.investigation_topic_for = old_topic
        site.raw_doc_count_for_articles = old_count

    single_row = (
        '<li class="nav-article-row"><a class="current" href="single-topic.html" '
        'title="Single Topic Article">Single Topic</a><em>1</em></li>'
    )
    assert single_row in nav
    assert '<summary><span>Single Topic</span>' not in nav
    assert '<details class="nav-subgroup"' in nav
    assert '<summary><span>Multi Topic</span><em>2</em></summary>' in nav
    assert 'href="multi-topic-a.html">Multi Topic A</a>' in nav
    assert 'href="multi-topic-b.html">Multi Topic B</a>' in nav
    print("ok test_single_article_topics_render_as_direct_rows_and_multi_topics_stay_grouped")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d build-site nav tests passed" % len(fns))
