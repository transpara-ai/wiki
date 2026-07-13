#!/usr/bin/env python3
"""Stdlib-assert tests for the Raw Area page (FO-WIKI-RAW-AREA v0.7.4 /
DF-DESIGN-WIKI-RAW-AREA v0.7.6) — the twenty-six named tests behind AC-T1..26.

Fixture policy (packet D6): tracked literals stay below both secret-scan
rules; every 64-hex value is GENERATED AT RUNTIME (hashlib over fixture
bytes) into temp-dir fixture trees — never committed.
"""
import datetime
import hashlib
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_site as site  # noqa: E402
import ingest_ops  # noqa: E402
import ingest_server  # noqa: E402


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_row(source_path, data=b"", **over):
    row = {
        "ingested_at": "2026-07-07T09:00:00+00:00",
        "mode": "browser-ingest",
        "target_slug": "",
        "source_path": source_path,
        "sha256": sha(data),
        "original_name": over.pop("original_name", source_path.rsplit("/", 1)[-1]),
        "note": "",
        "supersedes": "",
    }
    row.update(over)
    return row


def url_row(**over):
    row = {
        "ingested_at": "2026-07-07T09:00:00+00:00",
        "mode": "browser-ingest-url",
        "target_slug": "",
        "source_url": "https://example.invalid/doc",
        "note": "",
        "supersedes": "",
    }
    row.update(over)
    return row


class Tree:
    """A temp fixture tree shaped like the repo root (raw/inbox/...)."""

    def __init__(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._td.name)
        (self.root / "raw" / "inbox" / "manifest.d").mkdir(parents=True)

    def put(self, rel, data=b"doc"):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return rel

    def manifest(self, rows):
        (self.root / "raw" / "inbox" / "manifest.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in rows))

    def shard(self, name, rows):
        (self.root / "raw" / "inbox" / "manifest.d" / name).write_text(
            "".join((r if isinstance(r, str) else json.dumps(r)) + "\n" for r in rows))


def model(tree, refs=None):
    return site.raw_area_model(tree.root, refs)


def entry(m, rel):
    for _, bucket in m["groups"]:
        for e in bucket:
            if e["rel"] == rel:
                return e
    return None


# ---- AC-T1 / AC-T2 — membership ----

def test_raw_page_lists_exactly_the_enumerated_class():
    t = Tree()
    data = b"member"
    a = t.put("raw/inbox/2026-07-07/topic/doc.md", data)
    t.put("raw/inbox/2026-07-07/topic/stray.md", b"no evidence")
    b = t.put("raw/civilization/tai-res-2026-001-x-evaluation.md")
    t.manifest([file_row(a, data)])
    m = model(t)
    listed = {e["rel"] for _, bucket in m["groups"] for e in bucket}
    enumerated = set(site.raw_area_documents(
        t.root, {a: object()}))
    assert listed == enumerated == {a, b}, (listed, enumerated)
    print("ok test_raw_page_lists_exactly_the_enumerated_class")


def test_raw_page_membership_formula():
    t = Tree()
    data = b"evidence"
    rows = []
    # (a) evidence-less dated .md -> OUT
    t.put("raw/inbox/2026-07-13/topic/CONTROL.md")
    # (b) manifested .md -> IN
    b = t.put("raw/inbox/2026-07-13/topic/manifested.md", data)
    rows.append(file_row(b, data))
    # (c) manifested .txt -> IN
    c = t.put("raw/inbox/2026-07-13/topic/notes.txt", data)
    rows.append(file_row(c, data))
    # (d) upload-grammar .txt without row -> IN  /  (e) same for .md
    d = t.put("raw/inbox/2026-07-13/topic/report-%s.txt" % sha(b"d")[:12])
    e = t.put("raw/inbox/2026-07-13/topic/paper-%s.md" % sha(b"e")[:12])
    # (f) out-of-inbox tai-res -> IN
    f = t.put("raw/civilization/tai-res-2026-002-y-evaluation.md")
    # (g) control paths -> OUT (base manifest, shard, shard-dir README,
    #     generic inbox README, .gitkeep)
    t.put("raw/inbox/README.md")
    t.put("raw/inbox/.gitkeep")
    t.put("raw/inbox/manifest.d/README.md")
    # (h) control path WITH crafted evidence -> OUT (control precedence)
    ctl = "raw/inbox/README.md"
    rows.append(file_row(ctl, b"crafted"))
    # (i) non-md non-evidence stray -> OUT
    t.put("raw/inbox/2026-07-13/topic/draft.bin")
    # (j) rowless upload-grammar UNSERVABLE suffix -> IN
    j = t.put("raw/inbox/2026-07-13/topic/report-%s.bin" % sha(b"j")[:12])
    # (k) mixed-case TAI-RES -> IN
    k = t.put("raw/civilization/TAI-RES-2026-003-Z-Evaluation.md")
    k2 = t.put("raw/civilization/Tai-Res-2026-004-w-evaluation.md")
    # (l) MANIFESTED custom-named unservable -> IN (manifest lane suffix-agnostic)
    l = t.put("raw/inbox/2026-07-13/topic/notes.docx", data)
    rows.append(file_row(l, data))
    # (m) a tai-res-named SYMLINK escaping raw/ -> OUT (containment; CFAR r1)
    outside = t.root / "outside.md"
    outside.write_bytes(b"outside raw")
    link = t.root / "raw" / "civilization" / "tai-res-2026-009-link-evaluation.md"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(outside)
    t.manifest(rows)
    m = model(t)
    listed = {x["rel"] for _, bucket in m["groups"] for x in bucket}
    expected = {b, c, d, e, f, j, k, k2, l}
    assert listed == expected, listed.symmetric_difference(expected)
    print("ok test_raw_page_membership_formula")


# ---- AC-T3..T8 — dating, ordering, winner ----

def test_raw_page_groups_by_date_newest_first():
    t = Tree()
    data = b"x"
    early = t.put("raw/inbox/2026-07-01/t/a.md", data)
    late = t.put("raw/inbox/2026-07-02/t/b.md", data)
    # UTC basis: 23:30-05:00 on 07-02 == 04:30Z on 07-03 -> groups as 07-03
    mid = t.put("raw/inbox/2026-07-02/t/c.md", data)
    t.manifest([
        file_row(early, data, ingested_at="2026-07-01T10:00:00+00:00"),
        file_row(late, data, ingested_at="2026-07-02T10:00:00+00:00"),
        file_row(mid, data, ingested_at="2026-07-02T23:30:00-05:00"),
    ])
    m = model(t)
    order = [g for g, _ in m["groups"]]
    assert order == ["2026-07-03", "2026-07-02", "2026-07-01"], order
    print("ok test_raw_page_groups_by_date_newest_first")


def test_raw_page_entries_order_total_within_group():
    t = Tree()
    data = b"x"
    # (a) original-name primary order; (b) duplicate original names -> path order
    p1 = t.put("raw/inbox/2026-07-07/a/dup.md", data)
    p2 = t.put("raw/inbox/2026-07-07/b/dup.md", data)
    p3 = t.put("raw/inbox/2026-07-07/c/alpha.md", data)
    t.manifest([
        file_row(p1, data, original_name="same-name.md"),
        file_row(p2, data, original_name="same-name.md"),
        file_row(p3, data, original_name="alpha.md"),
    ])
    m = model(t)
    bucket = m["groups"][0][1]
    assert [e["rel"] for e in bucket] == [p3, p1, p2], [e["rel"] for e in bucket]
    print("ok test_raw_page_entries_order_total_within_group")


def test_raw_page_duplicate_row_winner_total_order():
    t = Tree()
    data = b"w"
    rel = t.put("raw/inbox/2026-07-07/t/doc.md", data)
    # (a) later ingested_at wins
    r_old = file_row(rel, data, ingested_at="2026-07-07T08:00:00+00:00", note="old")
    r_new = file_row(rel, data, ingested_at="2026-07-07T09:00:00+00:00", note="new")
    w, tie = site.raw_area_winner([
        site.raw_area_parse_row(json.dumps(r), "manifest.jsonl", 0, i + 1)[0]
        for i, r in enumerate((r_old, r_new))])
    assert w["note"] == "new" and tie is None
    # (b) equal instant across containers -> shard beats base; surfaced
    base = site.raw_area_parse_row(json.dumps(r_new), "manifest.jsonl", 0, 1)[0]
    shard = site.raw_area_parse_row(json.dumps(r_new), "manifest.d/s1.jsonl", 1, 1)[0]
    w, tie = site.raw_area_winner([base, shard])
    assert w["_container"] == "manifest.d/s1.jsonl" and tie
    # (c) equal instant same container -> line desc; surfaced
    l1 = site.raw_area_parse_row(json.dumps(r_new), "manifest.d/s1.jsonl", 1, 1)[0]
    l2 = site.raw_area_parse_row(json.dumps(r_new), "manifest.d/s1.jsonl", 1, 2)[0]
    w, tie = site.raw_area_winner([l1, l2])
    assert w["_line"] == 2 and tie
    # (d) full positional tie -> canonical digest decides, deterministically
    a = site.raw_area_parse_row(json.dumps(dict(r_new, note="a")), "m", 0, 1)[0]
    b = site.raw_area_parse_row(json.dumps(dict(r_new, note="b")), "m", 0, 1)[0]
    w1, tie1 = site.raw_area_winner([a, b])
    w2, _ = site.raw_area_winner([b, a])
    assert w1["note"] == w2["note"] and tie1
    print("ok test_raw_page_duplicate_row_winner_total_order")


def test_raw_page_manifest_date_beats_inbox_dir_date():
    t = Tree()
    data = b"x"
    rel = t.put("raw/inbox/2026-07-01/t/doc.md", data)  # dir says 07-01
    t.manifest([file_row(rel, data, ingested_at="2026-07-05T10:00:00+00:00")])
    m = model(t)
    e = entry(m, rel)
    assert e["group"] == "2026-07-05" and "ingested" in e["date_label"]
    print("ok test_raw_page_manifest_date_beats_inbox_dir_date")


def test_raw_page_unknown_date_falls_safe():
    t = Tree()
    rel = t.put("raw/civilization/tai-res-2026-005-q-evaluation.md")
    m = model(t)
    assert m["groups"][-1][0] is None, "unknown group must exist and sort last"
    e = entry(m, rel)
    assert e["group"] is None and e["date_label"] == "date unknown"
    print("ok test_raw_page_unknown_date_falls_safe")


def test_raw_page_shard_manifest_rows_are_read():
    t = Tree()
    data = b"sharded"
    rel = t.put("raw/inbox/2026-07-07/t/custom-name.rst", data)  # evidence only via shard row
    t.shard("s1.jsonl", [file_row(rel, data)])
    m = model(t)
    assert entry(m, rel) is not None, "shard row must confer membership (frozen-file law)"
    print("ok test_raw_page_shard_manifest_rows_are_read")


# ---- AC-T9..T13 — identity ----

def test_raw_page_identity_chain_and_labels():
    t = Tree()
    data = b"id"
    # (1) manifest identity
    a = t.put("raw/inbox/2026-07-07/t/a.md", data)
    # (2) sha12 filename identity (rowless)
    b = t.put("raw/inbox/2026-07-07/t/report-%s.md" % sha(b"b")[:12])
    # (3) computed identity, labeled (rowless tai-res)
    c = t.put("raw/civilization/tai-res-2026-006-r-evaluation.md", b"cbytes")
    t.manifest([file_row(a, data)])
    m = model(t)
    ea, eb, ec = entry(m, a), entry(m, b), entry(m, c)
    assert ea["id_source"] == "manifest" and ea["identity"] == sha(data)
    assert eb["id_source"] == "sha12" and eb["identity"] == sha(b"b")[:12]
    assert ec["id_source"] == "computed" and ec["identity"] == sha(b"cbytes")
    # rowless upload-grammar member: original name is the labeled
    # reconstruction, never the hashed storage basename
    assert eb["name"] == "report.md" and eb["name_label"] == "reconstructed from stored name"
    html_page = site.raw_page({"fresh": True, "text": ""}, m)
    assert "(computed)" in html_page
    # an OUT-OF-INBOX TAI-RES file that happens to end in -<12hex>.md keeps
    # its authored basename and takes the computed identity — the upload
    # grammar is meaningful only for dated-inbox members (CFAR r1)
    t2 = Tree()
    suffix12 = sha(b"authored")[:12]
    authored = t2.put(
        "raw/civilization/tai-res-2026-007-name-%s.md" % suffix12, b"authored bytes")
    m2 = model(t2)
    e2 = entry(m2, authored)
    assert e2["id_source"] == "computed" and e2["identity"] == sha(b"authored bytes")
    assert e2["name"] == authored.rsplit("/", 1)[-1] and e2["name_label"] is None
    print("ok test_raw_page_identity_chain_and_labels")


def test_raw_page_prefix_collision_disambiguates():
    t = Tree()
    # (a) two 64-hex manifest identities sharing a 12-hex display prefix
    d1, d2 = b"one", b"two"
    a = t.put("raw/inbox/2026-07-07/t/a.md", d1)
    b = t.put("raw/inbox/2026-07-07/t/b.md", d2)
    prefix = "0" * 12
    r1 = file_row(a, d1, sha256=prefix + sha(d1)[12:])
    r2 = file_row(b, d2, sha256=prefix + sha(d2)[12:])
    t.manifest([r1, r2])
    m = model(t)
    da, db = entry(m, a)["display_identity"], entry(m, b)["display_identity"]
    assert da != db and len(da) > 12 and len(db) > 12
    assert any("prefix collision" in x for x in m["anomalies"])
    # (b) a sha12-source identity colliding with a 64-hex identity's prefix:
    # the 64-hex side expands; the sha12 side (only 12 hex exist) appends the
    # labeled computed disambiguator. (Two DISTINCT sha12 identities can never
    # collide at display width — the display IS the full identity — and two
    # EQUAL sha12 identities take the D3 full-equality branch instead.)
    t2 = Tree()
    s = sha(b"s")[:12]
    d3 = b"manifested"
    x = t2.put("raw/inbox/2026-07-07/t/one-%s.md" % s, b"x1")  # sha12 identity s
    y = t2.put("raw/inbox/2026-07-07/u/two.md", d3)
    t2.manifest([file_row(y, d3, sha256=s + sha(d3)[12:])])   # 64-hex, same prefix
    m2 = model(t2)
    dx = entry(m2, x)["display_identity"]
    dy = entry(m2, y)["display_identity"]
    assert dx != dy, (dx, dy)
    assert "computed disambiguator" in dx, dx
    assert len(dy) > 12 and "disambiguator" not in dy, dy
    assert any("prefix collision" in a for a in m2["anomalies"])
    print("ok test_raw_page_prefix_collision_disambiguates")


def test_raw_page_current_identical_twins_cross_referenced():
    t = Tree()
    data = b"same bytes"
    a = t.put("raw/inbox/2026-07-07/t/a.md", data)
    b = t.put("raw/inbox/2026-07-07/u/b.md", data)
    t.manifest([file_row(a, data), file_row(b, data)])
    m = model(t)
    assert entry(m, a)["identical"] == 2 and entry(m, b)["identical"] == 2
    assert any("identical content ×2" in x for x in m["anomalies"])
    # identical CURRENT bytes under DIFFERENT recorded identities still
    # cross-reference — identity does not gate the computed grouping (CFAR r1)
    t2 = Tree()
    x = t2.put("raw/inbox/2026-07-07/t/x.md", data)
    y = t2.put("raw/inbox/2026-07-07/u/y.md", data)
    t2.manifest([file_row(x, data),
                 file_row(y, data, sha256=sha(b"different recorded"))])
    m2 = model(t2)
    assert entry(m2, x)["identical"] == 2 and entry(m2, y)["identical"] == 2
    assert entry(m2, y)["mismatch"], "the wrong-recorded twin still marks mismatch"
    print("ok test_raw_page_current_identical_twins_cross_referenced")


def test_raw_page_shared_recorded_identity_diverged_bytes():
    t = Tree()
    data = b"orig"
    a = t.put("raw/inbox/2026-07-07/t/a.md", data)
    b = t.put("raw/inbox/2026-07-07/u/b.md", b"diverged")  # bytes differ now
    t.manifest([file_row(a, data), file_row(b, data)])  # same recorded sha
    m = model(t)
    ea, eb = entry(m, a), entry(m, b)
    assert ea.get("shared_recorded") and eb.get("shared_recorded")
    assert not ea.get("identical") and not eb.get("identical"), \
        "diverged twins must never claim identical content"
    assert eb["mismatch"], "the diverged twin carries the mismatch mark"
    print("ok test_raw_page_shared_recorded_identity_diverged_bytes")


def test_raw_page_modified_since_ingest_mark_and_count():
    t = Tree()
    rel = t.put("raw/inbox/2026-07-07/t/doc.md", b"now")
    t.manifest([file_row(rel, b"at-ingest")])
    m = model(t)
    assert entry(m, rel)["mismatch"]
    assert any(x.startswith("modified since ingest: 1") for x in m["anomalies"])
    html_page = site.raw_page({"fresh": True, "text": ""}, m)
    assert "modified since ingest" in html_page
    # a rowless sha12-identity member whose bytes no longer match the stored
    # prefix also marks (CFAR r2); an unmodified one does not
    t2 = Tree()
    changed = t2.put("raw/inbox/2026-07-07/t/doc-%s.md" % sha(b"orig")[:12], b"changed")
    intact_bytes = b"intact"
    intact = t2.put("raw/inbox/2026-07-07/t/ok-%s.md" % sha(intact_bytes)[:12],
                    intact_bytes)
    m2 = model(t2)
    assert entry(m2, changed)["mismatch"], "sha12 drift must mark"
    assert not entry(m2, intact)["mismatch"], "matching sha12 must not mark"
    print("ok test_raw_page_modified_since_ingest_mark_and_count")


# ---- AC-T14..T18 — links, back-links, supersession ----

def test_raw_page_forward_links():
    t = Tree()
    data = b"f"
    served = t.put("raw/inbox/2026-07-07/t/doc.md", data)
    unserved = t.put("raw/inbox/2026-07-07/t/blob-%s.bin" % sha(b"u")[:12])
    t.manifest([file_row(served, data)])
    m = model(t)
    saved = site.SOURCE_LINKS
    try:
        site.SOURCE_LINKS = {served: "source/x.html"}
        html_page = site.raw_page({"fresh": True, "text": ""}, m)
    finally:
        site.SOURCE_LINKS = saved
    assert '<a href="source/x.html">' in html_page, "servable member must link"
    assert 'class="source-unserved"' in html_page, "unservable member degrades visibly"
    print("ok test_raw_page_forward_links")


def test_raw_page_backlink_union_all_four_fields():
    acc = {"backlinks": {}, "superseded": set()}
    fm = ("raw_documents:\n  - raw/inbox/2026-07-07/t/a.md\n"
          "superseded_raw_documents:\n  - raw/inbox/2026-07-07/t/b.md\n"
          "superseded_sources:\n  - raw/inbox/2026-07-07/t/c.md\n"
          "sources:\n  - raw/inbox/2026-07-07/t/d.md\n"
          "  - raw/transpara/doctrine.md\n")
    site.raw_area_fold_article(acc, fm, "topic", "Topic", False)
    for ref in ("raw/inbox/2026-07-07/t/a.md", "raw/inbox/2026-07-07/t/b.md",
                "raw/inbox/2026-07-07/t/c.md", "raw/inbox/2026-07-07/t/d.md"):
        assert acc["backlinks"].get(ref) == [("topic", "Topic", False)], ref
    assert "raw/transpara/doctrine.md" not in acc["backlinks"], \
        "doctrine citations are not class refs"
    print("ok test_raw_page_backlink_union_all_four_fields")


def test_raw_page_retired_backlinks_marked():
    t = Tree()
    data = b"r"
    rel = t.put("raw/inbox/2026-07-07/t/doc.md", data)
    t.manifest([file_row(rel, data)])
    refs = {"backlinks": {rel: [("old-topic", "Old Topic", True)]}, "superseded": set()}
    m = model(t, refs)
    html_page = site.raw_page({"fresh": True, "text": ""}, m)
    assert "Old Topic (retired)" in html_page
    assert '<a href="old-topic.html"' not in html_page, \
        "retired references must be NON-LINK (site link policy)"
    print("ok test_raw_page_retired_backlinks_marked")


def test_raw_page_unreferenced_file_marked_unassigned():
    t = Tree()
    data = b"u"
    rel = t.put("raw/inbox/2026-07-07/t/doc.md", data)
    t.manifest([file_row(rel, data)])
    m = model(t)
    html_page = site.raw_page({"fresh": True, "text": ""}, m)
    assert "unassigned — no topic references" in html_page
    print("ok test_raw_page_unreferenced_file_marked_unassigned")


def test_raw_page_superseded_marking_all_edges():
    data = b"s"
    # edges (1)-(3): article-side, via the fold
    for fm in (
        "superseded_raw_documents:\n  - raw/inbox/2026-07-07/t/doc.md\n",
        "superseded_sources:\n  - raw/inbox/2026-07-07/t/doc.md\n",
        "sources:\n  - raw/inbox/2026-07-07/t/new.md  # supersedes: raw/inbox/2026-07-07/t/doc.md\n",
    ):
        t = Tree()
        rel = t.put("raw/inbox/2026-07-07/t/doc.md", data)
        t.manifest([file_row(rel, data)])
        acc = {"backlinks": {}, "superseded": set()}
        site.raw_area_fold_article(acc, fm, "topic", "Topic", False)
        m = model(t, acc)
        assert entry(m, rel)["superseded"], "edge not honored: %s" % fm.split(":")[0]
    # edge (4): a newer valid manifest row's supersedes
    t = Tree()
    old = t.put("raw/inbox/2026-07-06/t/doc-v1.md", data)
    new = t.put("raw/inbox/2026-07-07/t/doc-v2.md", data)
    t.manifest([file_row(old, data),
                file_row(new, data, supersedes=old,
                         ingested_at="2026-07-07T10:00:00+00:00")])
    m = model(t)
    assert entry(m, old)["superseded"], "manifest supersedes edge not honored"
    # edge (4) also holds for a URL-shape row's supersedes (a URL re-ingest
    # can be the only record superseding a raw doc — CFAR r2)
    t2 = Tree()
    doc = t2.put("raw/inbox/2026-07-06/t/doc.md", data)
    t2.manifest([file_row(doc, data), url_row(supersedes=doc)])
    m2 = model(t2)
    assert entry(m2, doc)["superseded"], "URL-row supersedes edge not honored"
    print("ok test_raw_page_superseded_marking_all_edges")


# ---- AC-T19..T23 — reader lanes, anomalies, escaping ----

def test_raw_page_manifest_rejection_lanes():
    ok_file = file_row("raw/inbox/2026-07-07/t/doc.md", b"x")
    ok_url = url_row()
    lanes = []
    # parse-level lanes first
    lanes.append(("", "blank"))
    lanes.append(("{not json", "unreadable"))
    lanes.append(("[1, 2]", "non-object"))
    lanes.append(('{"a": 1, "a": 2}', "unreadable"))  # duplicate keys
    # each required file-row key removed
    for key in sorted(site.RAW_AREA_FILE_ROW_KEYS):
        bad = {k: v for k, v in ok_file.items() if k != key}
        lanes.append((json.dumps(bad), "unknown row shape"))
    # each required URL-row key removed
    for key in sorted(site.RAW_AREA_URL_ROW_KEYS):
        bad = {k: v for k, v in ok_url.items() if k != key}
        lanes.append((json.dumps(bad), "unknown row shape"))
    lanes.append((json.dumps(dict(ok_file, extra="x")), "unknown row shape"))
    hybrid = dict(ok_file)
    hybrid["source_url"] = "https://example.invalid/x"
    lanes.append((json.dumps(hybrid), "unknown row shape"))
    lanes.append((json.dumps(dict(ok_file, mode=7)), "non-string"))
    lanes.append((json.dumps(dict(ok_file, source_path="  ")), "blank required"))
    lanes.append((json.dumps(dict(ok_file, sha256="abc123")), "not 64-hex"))
    lanes.append((json.dumps(dict(ok_file, ingested_at="2026-07-07T09:00:00")), "naive"))
    lanes.append((json.dumps(dict(ok_file, ingested_at="not-a-date+00:00")), "unparseable"))
    lanes.append((json.dumps(dict(ok_file, ingested_at="2026-02-30T09:00:00+00:00")),
                  "unparseable"))
    # boundary offset overflows UTC normalization -> rejected, never a crash
    lanes.append((json.dumps(dict(ok_file, ingested_at="0001-01-01T00:00:00+23:59")),
                  "non-normalizable"))
    # parser recursion from deep nesting -> rejected row, never a build abort
    lanes.append(("[" * 100000 + "]" * 100000, "unreadable"))
    # an escaped lone surrogate would crash UTF-8 encoding at write time
    lanes.append((json.dumps(dict(ok_file, original_name="bad\ud800.md")),
                  "unencodable"))
    for line, needle in lanes:
        row, anomaly = site.raw_area_parse_row(line, "m", 0, 1)
        assert row is None and anomaly and needle in anomaly, (line[:60], anomaly)
    # acceptance: valid rows with blank optional fields
    for base in (ok_file, ok_url):
        good = dict(base, note="", supersedes="", target_slug="")
        row, anomaly = site.raw_area_parse_row(json.dumps(good), "m", 0, 1)
        assert row is not None and anomaly is None, anomaly
    # rejected rows contribute nothing and never crash the model
    t = Tree()
    member = t.put("raw/inbox/2026-07-07/t/doc.md", b"x")
    t.manifest([file_row(member, b"x")])
    t.shard("bad.jsonl", ["{not json", json.dumps(dict(ok_file, sha256="short"))])
    m = model(t)
    assert entry(m, member) is not None
    assert sum(1 for a in m["anomalies"] if "unreadable manifest line" in a) == 1
    assert sum(1 for a in m["anomalies"] if "not 64-hex" in a) == 1
    # a corrupt BYTE rejects only its own line; valid neighbors survive
    t2 = Tree()
    kept = t2.put("raw/inbox/2026-07-07/t/kept.md", b"k")
    good = json.dumps(file_row(kept, b"k")).encode()
    (t2.root / "raw" / "inbox" / "manifest.jsonl").write_bytes(
        b'{"broken": "\xff\xfe"}\n' + good + b"\n")
    m2 = model(t2)
    assert entry(m2, kept) is not None, "valid neighbor line must survive"
    assert sum(1 for a in m2["anomalies"] if "undecodable manifest line" in a) == 1
    print("ok test_raw_page_manifest_rejection_lanes")


def test_raw_page_url_rows_counted_not_listed():
    t = Tree()
    data = b"x"
    member = t.put("raw/inbox/2026-07-07/t/doc.md", data)
    t.manifest([file_row(member, data),
                url_row(source_url="https://example.invalid/<script>")])
    m = model(t)
    listed = {e["rel"] for _, bucket in m["groups"] for e in bucket}
    assert listed == {member}, "URL rows must never produce a document entry"
    assert any(x.startswith("URL ingests: 1") for x in m["anomalies"])
    html_page = site.raw_page({"fresh": True, "text": ""}, m)
    assert "https://example.invalid/&lt;script&gt;" in html_page, \
        "the footer lists the URL, escaped"
    print("ok test_raw_page_url_rows_counted_not_listed")


def test_raw_page_absent_manifest_target_surfaced():
    t = Tree()
    t.manifest([file_row("raw/inbox/2026-07-07/t/gone.md", b"gone")])
    m = model(t)
    assert any("recorded but absent on disk" in x for x in m["anomalies"])
    print("ok test_raw_page_absent_manifest_target_surfaced")


def test_raw_page_anomaly_warnings_emitted():
    # main() prints exactly one "raw-area warning:" line per model anomaly;
    # this asserts the 1:1 contract's substrate — one anomaly entry per
    # exercised lane, no batching and no suppression.
    t = Tree()
    member = t.put("raw/inbox/2026-07-07/t/doc.md", b"now")
    t.manifest([file_row(member, b"then"),
                file_row("raw/inbox/2026-07-07/t/gone.md", b"gone"),
                url_row()])
    t.shard("bad.jsonl", ["{not json"])
    m = model(t)
    for needle in ("modified since ingest: 1", "recorded but absent on disk",
                   "URL ingests: 1", "unreadable manifest line"):
        assert sum(1 for a in m["anomalies"] if needle in a) == 1, needle
    print("ok test_raw_page_anomaly_warnings_emitted")


def test_raw_page_rendered_fields_escaped_and_bounded():
    t = Tree()
    data = b"esc"
    rel = t.put("raw/inbox/2026-07-07/t/doc.md", data)
    t.manifest([
        file_row(rel, data, original_name="<b>name</b>.md",
                 note="SECRET-NOTE-VALUE", mode="browser-ingest"),
        file_row("raw/inbox/2026-07-07/t/<i>gone</i>.md", data),
        url_row(source_url="https://example.invalid/<u>x</u>"),
    ])
    m = model(t)
    html_page = site.raw_page({"fresh": True, "text": ""}, m)
    assert "&lt;b&gt;name&lt;/b&gt;.md" in html_page and "<b>name</b>" not in html_page
    assert "&lt;i&gt;gone&lt;/i&gt;" in html_page and "<i>gone</i>" not in html_page
    assert "&lt;u&gt;x&lt;/u&gt;" in html_page and "<u>x</u>" not in html_page
    assert "SECRET-NOTE-VALUE" not in html_page, "note is never rendered"
    print("ok test_raw_page_rendered_fields_escaped_and_bounded")


# ---- AC-T24..T26 — nav and route integration ----

def test_raw_page_single_nav_entry_both_variants():
    top = site.top_links()
    assert top.count('href="raw.html"') == 1, "exactly one root-variant anchor"
    assert top.count("<a ") == top.count("</a>") == 4, \
        "Repos/Sources/Raw/Ingest and nothing else"
    import inspect
    simple = inspect.getsource(site.simple_page)
    assert simple.count('href="../raw.html"') == 1, "exactly one ../ variant anchor"
    print("ok test_raw_page_single_nav_entry_both_variants")


def test_raw_route_reserved_in_creation_guard():
    assert ingest_server.RESERVED_GENERATED_ROUTES == frozenset(("raw",)), \
        "the reserved set is EXACTLY {raw} for this order"
    assert ingest_server.subject_absent("Raw") is False, \
        "an investigation named Raw must be refused"
    assert ingest_server.subject_absent("raw") is False
    # denial-only control: a name the set does not touch still creates
    assert ingest_server.subject_absent("Entirely Novel Fixture Subject 9Q") is True
    print("ok test_raw_route_reserved_in_creation_guard")


def test_raw_route_classified_as_builder_page():
    assert "raw" in ingest_ops.BUILDER_PAGES
    got = ingest_ops.canonical_article_target("raw.html", meta={})
    assert got == ("page", "raw"), got
    # mirrors the existing tool routes
    assert ingest_ops.canonical_article_target("sources.html", meta={}) == ("page", "sources")
    print("ok test_raw_route_classified_as_builder_page")


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

if __name__ == "__main__":
    for fn in TESTS:
        fn()
    print("all %d raw-area tests passed" % len(TESTS))
