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

# REPOS is populated by main() at build time, not at import. Seed
# deterministic fixture records (one per group) so the sidebar/repo-nav tests
# exercise the populated path WITHOUT depending on host-local sibling
# checkouts — a clean CI runner has no /Transpara/transpara-ai/repos tree
# (CFAR r3).
build_site.REPOS = [
    {"name": "acme-tool", "slug": "acme-tool",
     "href": "repo-acme-tool.html", "group": "platform"},
    {"name": "acme-hive", "slug": "acme-hive",
     "href": "repo-acme-hive.html", "group": "civilization"},
    {"name": "acme-misc", "slug": "acme-misc",
     "href": "repo-acme-misc.html", "group": "other"},
]


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

    # ---- TC3 (AC1): the real corpus has explicit registry-valid placement ----
    def test_real_corpus_uses_explicit_registry_metadata(self):
        # Build import proves the catalog accepted every real page. Original
        # Civilization pages and curated transpara-owned seeds share one catalog;
        # neither may rely on compatibility inference.
        explicit = 0
        for p in sorted((BASE / "wiki").glob("*.md")):
            fm = p.read_text().split("---", 2)[1]
            self.assertRegex(fm, r"(?m)^org\s*:\s*(transpara|transpara-ai)\s*$")
            self.assertRegex(fm, r"(?m)^primary_placement\s*:\s*(civilization|platform|competition|devops)/")
            self.assertRegex(fm, r"(?m)^placements\s*:")
            self.assertRegex(fm, r"(?m)^classification\s*:\s*(internal|company-internal|public-candidate)\s*$")
            m = re.search(r"(?m)^tier\s*:\s*([^#\n]+)", fm)
            tier = m.group(1).strip().strip('"').strip("'")
            self.assertEqual(build_site.META[p.stem]["tier"], tier)
            meta = build_site.META[p.stem]
            space = meta["primary_placement"].split("/", 1)[0]
            self.assertEqual(
                build_site.STRUCTURE.space_map[space].steward, meta["org"])
            self.assertIn(meta["primary_placement"], meta["placements"])
            explicit += 1
        self.assertGreaterEqual(explicit, 131)
        # A page with no legacy tier and no explicit placement fails loudly.
        with tempfile.TemporaryDirectory() as tmp:
            page(tmp, "no-tier", ["entity: N"])
            with wiki_root(build_site, tmp):
                with self.assertRaises(SystemExit):
                    build_site.article_meta()

    # ---- TC4 (AC4): space-scoped navigation follows the central registry ----
    def test_sidebar_two_org_bands(self):
        html_out = build_site.build_sidebar("", active_space="civilization")
        self.assertIn('aria-label="Transpara Knowledge Hub navigation"', html_out)
        self.assertIn('Transpara-AI · Civilization', html_out)
        self.assertIn('data-section="civilization/foundational"', html_out)
        self.assertNotIn('data-section="platform/product-overview"', html_out)
        # A shared article appears in each placement's navigation without
        # cloning the underlying article or changing its canonical route.
        old_meta = build_site.META
        try:
            build_site.META = dict(build_site.META, **{
                "acme-org": {"slug": "acme-org", "title": "Acme Org",
                             "tier": "concept", "org": "transpara-ai",
                             "primary_placement": "civilization/concept",
                             "placements": ["civilization/concept",
                                            "competition/competitors"],
                             "classification": "internal",
                             "retired_on": ""}})
            navbox = build_site.build_navbox(active_space="competition")
        finally:
            build_site.META = old_meta
        self.assertIn('href="acme-org.html"', navbox)
        self.assertIn('<span class="navbox-grp">Competitors</span>', navbox)

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

    # ---- TC6 (AC5): the registry-backed placement gate fails closed ----
    def test_ingest_org_section_fail_closed(self):
        v = ingest_server.validate_placement
        refused = ingest_ops.OpRefused
        # Missing, unknown, mixed-case, foreign-section and unknown-steward
        # inputs all refuse for either route intent.
        for space, section, steward in [
                ("", "", ""), ("", "product-overview", "transpara"),
                ("platfrom", "capabilities", "transpara"),
                ("Platform", "capabilities", "transpara"),
                ("platform", "concept", "transpara"),
                ("civilization", "product-overview", "transpara-ai"),
                ("civilization", "concept", "Transpara-AI"),
                ("competition", "", "transpara")]:
            for new_inv in (False, True):
                with self.assertRaises(
                        refused, msg=(space, section, steward, new_inv)):
                    v(space, section, steward, new_inv)
        v("platform", "product-overview", "transpara", False)
        v("civilization", "concept", "transpara-ai", False)
        v("civilization", "investigation", "transpara-ai", True)
        for space, section, steward in [
                ("platform", "product-overview", "transpara"),
                ("competition", "competitors", "transpara"),
                ("civilization", "concept", "transpara-ai")]:
            with self.assertRaises(refused):
                v(space, section, steward, True)
        # target coherence: destination truth lives on the page
        with tempfile.TemporaryDirectory() as tmp:
            page(tmp, "existing", ["entity: E", "tier: concept"])
            with wiki_root(ingest_server, tmp):
                ingest_server.check_target_placement(
                    "existing", "civilization", "concept", "transpara-ai")
                with self.assertRaises(refused):
                    ingest_server.check_target_placement(
                        "existing", "civilization", "architecture", "transpara-ai")
                with self.assertRaises(refused):
                    ingest_server.check_target_placement(
                        "existing", "competition", "competitors", "transpara")
                # no page -> nothing to contradict (unassigned lane)
                ingest_server.check_target_placement(
                    "absent", "civilization", "concept", "transpara-ai")

    # ---- TC7 (AC6): current placement rows and historical rows both parse ----
    def test_ingest_ledger_records_org_section(self):
        base = {"ts": "2026-07-10T12:00:00+00:00", "operation": "add",
                "slug": "existing", "sources": ["raw/x.md"], "created": False,
                "rebuild": "ok"}
        ingest_ops._validate_ledger_row(dict(base))  # historical shape parses
        historical = dict(base, org="transpara", section="product")
        ingest_ops._validate_ledger_row(historical)
        new = dict(base, space="platform", section="product-overview",
                   steward="transpara", placement="platform/product-overview")
        ingest_ops._validate_ledger_row(new)
        for bad in (
                dict(base, space="platform", section="product-overview"),
                dict(base, space="", section="product-overview",
                     steward="transpara", placement="platform/product-overview"),
                dict(base, space="platform", section="product-overview",
                     steward="transpara", placement="platform/capabilities"),
                dict(base, space="bogus", section="product-overview",
                     steward="transpara", placement="bogus/product-overview"),
                dict(base, space="platform", section="product-overview",
                     steward="bogus", placement="platform/product-overview"),
                dict(base, orgg="x")):
            with self.assertRaises(ingest_ops.OpRefused, msg=bad):
                ingest_ops._validate_ledger_row(bad)
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "ledger.jsonl"
            ingest_ops.append_ledger(path, new)
            row = json.loads(path.read_text().strip().splitlines()[-1])
        self.assertEqual(row["space"], "platform")
        self.assertEqual(row["placement"], "platform/product-overview")

    # ---- TC8 (AC7): ingest UI presents registry-backed placement fields ----
    def test_ingest_ui_org_section_fields(self):
        html_out = build_site.ingest_page({})
        self.assertIn('id="ingest-space"', html_out)
        self.assertIn('id="ingest-section"', html_out)
        self.assertIn('id="ingest-steward"', html_out)
        self.assertRegex(html_out, r'<select name="space" id="ingest-space" required>')
        self.assertRegex(html_out, r'<select name="section" id="ingest-section" required>')
        self.assertRegex(html_out, r'<input name="steward" id="ingest-steward" readonly required>')
        for space in build_site.STRUCTURE.spaces:
            self.assertIn('<option value="%s">' % space.key, html_out)
            self.assertIn(space.steward, html_out)

    # ---- TC9 (AC6): raw-doc registrations carry placement + steward ----
    def test_ingest_rawdoc_registration_carries_org_section(self):
        line = ingest_server.source_line(
            "raw/inbox/x.md", "a note", "", "platform",
            "product-overview", "transpara")
        self.assertIn("placement: platform/product-overview", line)
        self.assertIn("steward: transpara", line)
        self.assertIn('"raw/inbox/x.md"', line)
        # and through the real append path on a real page file
        with tempfile.TemporaryDirectory() as tmp:
            page(tmp, "existing",
                 ["entity: E", "tier: concept", "sources:",
                  '  - "raw/inbox/old.md"'])
            with wiki_root(ingest_server, tmp):
                added = ingest_server.append_sources_to_article(
                    "existing", ["raw/inbox/new.md"], "n", "",
                    space="civilization", section="concept",
                    steward="transpara-ai")
            text = (pathlib.Path(tmp) / "existing.md").read_text()
        self.assertEqual(added, ["raw/inbox/new.md"])
        self.assertIn(
            "placement: civilization/concept; steward: transpara-ai", text)
        # the CREATE route's seed source line carries the pair too — the later
        # append skips the seed as already-present, so it must ride the
        # skeleton itself (CFAR r1 P2)
        with tempfile.TemporaryDirectory() as tmp:
            with wiki_root(ingest_server, tmp):
                slug, created = ingest_server.create_article_from_source(
                    "raw/inbox/2026-07-10/x/doc.md", "seed note",
                    name="Seed Topic", space="civilization",
                    section="investigation", steward="transpara-ai")
                seed_text = (pathlib.Path(tmp) / ("%s.md" % slug)).read_text()
        self.assertTrue(created)
        self.assertIn("org: transpara-ai", seed_text)
        self.assertIn("primary_placement: civilization/investigation", seed_text)
        self.assertIn(
            "placement: civilization/investigation; steward: transpara-ai",
            seed_text)


if __name__ == "__main__":
    unittest.main()
