"""TC1–TC9 for DP-20260710-wiki-org-sections (org bands + org/section ingest).

Loads the real modules from compile/ (inflight.test.py pattern). build_site is
loaded ONCE against the real corpus — that import itself proves the strict
org/tier validation accepts every existing page (AC1); fixture-directory cases
then monkeypatch the module's WIKI root, never the repo's own pages.
"""
import contextlib
import importlib.util
import json
import pathlib
import re
import tempfile
import unittest

BASE = pathlib.Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(
        name, BASE / "compile" / ("%s.py" % name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


org_structure = load("org_structure")
build_site = load("build_site")
ingest_server = load("ingest_server")
# the SAME module instance ingest_server raises from (a second file-loaded
# copy would make OpRefused a different class and break assertRaises)
ingest_ops = ingest_server.ingest_ops

# REPOS is populated by main() at build time, not at import — fill it so the
# sidebar/repo-nav tests exercise the populated path like a real build does.
build_site.REPOS = build_site.repo_records()


def page(tmp, slug, fm_lines):
    p = pathlib.Path(tmp) / ("%s.md" % slug)
    p.write_text("---\n" + "\n".join(fm_lines) + "\n---\n\nbody\n")
    return p


@contextlib.contextmanager
def wiki_root(module, tmp):
    old = module.WIKI
    module.WIKI = pathlib.Path(tmp)
    try:
        yield
    finally:
        module.WIKI = old


class TestOrgSections(unittest.TestCase):

    # ---- TC1 (AC2): unknown/empty/mixed-case org fails the build loudly ----
    def test_build_rejects_unknown_org(self):
        for bad in ("transporo", "", "Transpara", "TRANSPARA-AI"):
            with self.assertRaises(ValueError) as ctx:
                org_structure.resolve_org_tier("some-page", True, bad, "concept")
            msg = str(ctx.exception)
            self.assertIn("some-page", msg)
            self.assertIn("transpara", msg)  # allowlist named in the error
        # builder level: a fixture page with an unknown org kills article_meta
        with tempfile.TemporaryDirectory() as tmp:
            page(tmp, "bad-org", ["entity: Bad", "org: transporo", "tier: concept"])
            with wiki_root(build_site, tmp):
                with self.assertRaises(SystemExit):
                    build_site.article_meta()
        # inline comments strip like the tier machinery (fm_scalar)
        with tempfile.TemporaryDirectory() as tmp:
            page(tmp, "ok-comment",
                 ["entity: Ok", "org: transpara # note", "tier: organization"])
            with wiki_root(build_site, tmp):
                meta = build_site.article_meta()
        self.assertEqual(meta["ok-comment"]["org"], "transpara")

    # ---- TC2 (AC3): org/tier mismatch fails; valid pairs land correctly ----
    def test_build_rejects_org_section_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            page(tmp, "mismatch",
                 ["entity: M", "org: transpara", "tier: investigation"])
            with wiki_root(build_site, tmp):
                with self.assertRaises(SystemExit):
                    build_site.article_meta()
        with tempfile.TemporaryDirectory() as tmp:
            page(tmp, "org-page",
                 ["entity: O", "org: transpara", "tier: organization"])
            page(tmp, "prod-page",
                 ["entity: P", "org: transpara", "tier: product"])
            with wiki_root(build_site, tmp):
                meta = build_site.article_meta()
        self.assertEqual(meta["org-page"]["org"], "transpara")
        self.assertEqual(meta["prod-page"]["tier"], "product")
        with tempfile.TemporaryDirectory() as tmp:
            page(tmp, "wrong-way",
                 ["entity: W", "org: transpara-ai", "tier: organization"])
            with wiki_root(build_site, tmp):
                with self.assertRaises(SystemExit):
                    build_site.article_meta()

    # ---- TC3 (AC1): the real corpus is unchanged; the fallback is gone ----
    def test_legacy_pages_unchanged(self):
        # build_site imported fine at module load — the strict gate accepted
        # every real page. Now prove the inventory matches an independent scan
        # and that every page defaulted to the transpara-ai org.
        expected = {}
        for p in sorted((BASE / "wiki").glob("*.md")):
            fm = p.read_text().split("---", 2)[1]
            m = re.search(r"(?m)^tier\s*:\s*([^#\n]+)", fm)
            expected[p.stem] = m.group(1).strip().strip('"').strip("'")
            self.assertIsNone(re.search(r"(?m)^org\s*:", fm),
                              "%s unexpectedly declares org" % p.stem)
        got = {s: m["tier"] for s, m in build_site.META.items()}
        self.assertEqual(expected, got)
        self.assertTrue(all(m["org"] == "transpara-ai"
                            for m in build_site.META.values()))
        # the removed `concept` fallback: a page with NO tier now fails loudly
        with tempfile.TemporaryDirectory() as tmp:
            page(tmp, "no-tier", ["entity: N"])
            with wiki_root(build_site, tmp):
                with self.assertRaises(SystemExit):
                    build_site.article_meta()

    # ---- TC4 (AC4): two org bands in mock order, sections org-scoped ----
    def test_sidebar_two_org_bands(self):
        html_out = build_site.build_sidebar("")
        t = html_out.find('<div class="side-org">Transpara</div>')
        tai = html_out.find('<div class="side-org">Transpara-AI</div>')
        self.assertGreater(t, -1)
        self.assertGreater(tai, t, "TRANSPARA band must render above TRANSPARA-AI")
        # no transpara articles exist yet -> its article sections are skipped
        self.assertNotIn('data-tier="organization"', html_out)
        self.assertNotIn('data-tier="product"', html_out)
        # the transpara-ai band keeps its tier groups
        self.assertIn('data-tier="foundational"', html_out)
        # every nav surface includes Transpara sections when populated: the
        # bottom navbox must list a transpara page, not only TIER_ORDER rows
        # (CFAR r2)
        old_meta = build_site.META
        try:
            build_site.META = dict(build_site.META, **{
                "acme-org": {"slug": "acme-org", "title": "Acme Org",
                             "tier": "organization", "org": "transpara",
                             "retired_on": ""}})
            navbox = build_site.build_navbox()
        finally:
            build_site.META = old_meta
        self.assertIn('href="acme-org.html"', navbox)
        self.assertIn('<span class="navbox-grp">Organization</span>', navbox)

    # ---- TC5 (AC4): repos split by org, nothing dropped or duplicated ----
    def test_repo_nav_split_by_org(self):
        grouped = build_site.repos_by_group()
        nav_t = build_site.build_repo_nav("", org="transpara")
        nav_ai = build_site.build_repo_nav("", org="transpara-ai")
        for repo in grouped.get("platform", []):
            marker = ">%s</a>" % build_site.html.escape(repo["name"])
            self.assertIn(marker, nav_t)
            self.assertNotIn(marker, nav_ai)
        for group in ("civilization", "other"):
            for repo in grouped.get(group, []):
                marker = ">%s</a>" % build_site.html.escape(repo["name"])
                self.assertIn(marker, nav_ai)
                self.assertNotIn(marker, nav_t)
        counts = [int(m) for m in re.findall(r"<em>(\d+)</em>", nav_t + nav_ai)]
        self.assertEqual(sum(counts), len(build_site.REPOS),
                         "every repo appears under exactly one org band")
        # repos.html ("index") keeps the pre-split open behavior: current on
        # the band hosting the overview link, and only there (CFAR r1 P3)
        self.assertIn('data-current-group="true"',
                      build_site.build_repo_nav("index", org="transpara-ai"))
        self.assertNotIn('data-current-group="true"',
                         build_site.build_repo_nav("index", org="transpara"))

    # ---- TC6 (AC5): the full fail-closed input matrix ----
    def test_ingest_org_section_fail_closed(self):
        v = ingest_server.validate_org_section
        refused = ingest_ops.OpRefused
        # {missing, empty, unknown, mixed-case, foreign-section} x new_investigation
        for org, section in [("", ""), ("", "organization"),
                             ("transporo", "concept"),
                             ("Transpara", "organization"),
                             ("TRANSPARA-AI", "concept"),
                             ("transpara", "concept"),
                             ("transpara", "investigation"),
                             ("transpara-ai", "organization"),
                             ("transpara-ai", "")]:
            for new_inv in (False, True):
                with self.assertRaises(refused, msg=(org, section, new_inv)):
                    v(org, section, new_inv)
        # valid pairs accepted (no exception, no I/O by construction)
        v("transpara", "organization", False)
        v("transpara", "product", False)
        v("transpara-ai", "concept", False)
        v("transpara-ai", "investigation", True)
        # new-investigation coherence: valid pairs that are NOT
        # (transpara-ai, investigation) still refuse when the flag is on
        for org, section in [("transpara", "organization"),
                             ("transpara", "product"),
                             ("transpara-ai", "concept")]:
            with self.assertRaises(refused):
                v(org, section, True)
        # target coherence: destination truth lives on the page
        with tempfile.TemporaryDirectory() as tmp:
            page(tmp, "existing", ["entity: E", "tier: concept"])
            with wiki_root(ingest_server, tmp):
                ingest_server.check_target_org_section(
                    "existing", "transpara-ai", "concept")  # matches -> passes
                with self.assertRaises(refused):
                    ingest_server.check_target_org_section(
                        "existing", "transpara-ai", "architecture")
                with self.assertRaises(refused):
                    ingest_server.check_target_org_section(
                        "existing", "transpara", "organization")
                # no page -> nothing to contradict (unassigned lane)
                ingest_server.check_target_org_section(
                    "absent", "transpara-ai", "concept")

    # ---- TC7 (AC6): ledger rows carry org+section; old rows still parse ----
    def test_ingest_ledger_records_org_section(self):
        base = {"ts": "2026-07-10T12:00:00+00:00", "operation": "add",
                "slug": "existing", "sources": ["raw/x.md"], "created": False,
                "rebuild": "ok"}
        ingest_ops._validate_ledger_row(dict(base))  # historical shape parses
        new = dict(base, org="transpara", section="product")
        ingest_ops._validate_ledger_row(new)  # additive shape parses
        for bad in (dict(base, org=""),                       # empty value
                    dict(base, org="transpara"),              # org w/o section is
                    dict(base, section="product"),            # fine (independent)
                    dict(base, orgg="x")):                    # foreign key
            if "orgg" in bad or bad.get("org") == "":
                with self.assertRaises(ingest_ops.OpRefused):
                    ingest_ops._validate_ledger_row(bad)
            else:
                ingest_ops._validate_ledger_row(bad)
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "ledger.jsonl"
            ingest_ops.append_ledger(path, new)
            row = json.loads(path.read_text().strip().splitlines()[-1])
        self.assertEqual(row["org"], "transpara")
        self.assertEqual(row["section"], "product")

    # ---- TC8 (AC7): ingest UI presents org-scoped required dropdowns ----
    def test_ingest_ui_org_section_fields(self):
        html_out = build_site.ingest_page({})
        self.assertIn('id="ingest-org"', html_out)
        self.assertIn('id="ingest-section"', html_out)
        self.assertRegex(html_out, r'<select name="org" id="ingest-org" required>')
        self.assertRegex(html_out, r'<select name="section" id="ingest-section" required>')
        for org in org_structure.ORG_ORDER:
            self.assertIn('<option value="%s">' % org, html_out)
        # the section options the JS swaps in come from the same declaration
        self.assertIn(json.dumps(org_structure.ORG_SECTIONS, sort_keys=True), html_out)

    # ---- TC9 (AC6): raw-doc registration lines carry org+section ----
    def test_ingest_rawdoc_registration_carries_org_section(self):
        line = ingest_server.source_line(
            "raw/inbox/x.md", "a note", "", "transpara", "product")
        self.assertIn("org: transpara", line)
        self.assertIn("section: product", line)
        self.assertIn('"raw/inbox/x.md"', line)
        # and through the real append path on a real page file
        with tempfile.TemporaryDirectory() as tmp:
            page(tmp, "existing",
                 ["entity: E", "tier: concept", "sources:",
                  '  - "raw/inbox/old.md"'])
            with wiki_root(ingest_server, tmp):
                added = ingest_server.append_sources_to_article(
                    "existing", ["raw/inbox/new.md"], "n", "",
                    org="transpara-ai", section="concept")
            text = (pathlib.Path(tmp) / "existing.md").read_text()
        self.assertEqual(added, ["raw/inbox/new.md"])
        self.assertIn("org: transpara-ai; section: concept", text)
        # the CREATE route's seed source line carries the pair too — the later
        # append skips the seed as already-present, so it must ride the
        # skeleton itself (CFAR r1 P2)
        with tempfile.TemporaryDirectory() as tmp:
            with wiki_root(ingest_server, tmp):
                slug, created = ingest_server.create_article_from_source(
                    "raw/inbox/2026-07-10/x/doc.md", "seed note",
                    name="Seed Topic", org="transpara-ai",
                    section="investigation")
                seed_text = (pathlib.Path(tmp) / ("%s.md" % slug)).read_text()
        self.assertTrue(created)
        self.assertIn("org: transpara-ai; section: investigation", seed_text)


if __name__ == "__main__":
    unittest.main()
