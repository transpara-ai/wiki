"""Trust, ownership, replay, and command tests for Wiki verification.

The 30 historical subjects are exact first-parent main commits. Synthetic
subjects are labeled separately and exercise the enabled documentation bundle
at least five times. The tests prove that source, controls, unknown domains,
and every unowned tracked file remain full while focused commands omit the
static-site, service, deployment, release, browser, and ingestion suites.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    """Load one repository module without requiring package installation."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SELECTOR = load_module("wiki_selector", ROOT / "verification" / "select_verify.py")
ADAPTER = load_module("wiki_adapter", ROOT / "tools" / "verification_adapter.py")
RUNNER = load_module(
    "wiki_bundle_runner", ROOT / "tools" / "run_verification_bundles.py"
)
CHECKER = load_module(
    "wiki_contract_checker", ROOT / "tools" / "check_repository_contracts.py"
)

HISTORICAL_HEADS = (
    ("historical: merge terminology workspace", "3b447a4f0a7c73cdef4bf12146f1a0b0df6e17b1"),
    ("historical: merge terminology checksums", "ac50f7b774a4f53602c09983291edd7a23fdede9"),
    ("historical: adopt TLC 0.1.3", "0712edf235236041df03149fa77693cbdd51378d"),
    ("historical: add architecture comparison", "38b9183661475406eed03d7d88983575fb7f389d"),
    ("historical: clear v0.9 checksums", "99cc99d8593d7a3ad51bdb8f9e123bd2c490bdfc"),
    ("historical: release and pattern audit", "5665e1cfc2974283bfe117f362684440b7c5eb5f"),
    ("historical: clear v0.8.3 checksums", "daee3ece6f9d559ff106b619a91aa9402f04d164"),
    ("historical: define provider boundary", "cc29aa12c5dc216416a62249d9413e341c909a42"),
    ("historical: clear v0.8.2 checksums", "7f43f25d130099c509304ab90dd7ddecb08cc804"),
    ("historical: add loopback profile origin", "7743d96f99830aa80ce23e80d1a624ad8262eefb"),
    ("historical: add enter-to-ask", "3dede045ef0c090d54db5c8c088bfe08427cfd6f"),
    ("historical: clear v0.8.1 checksums", "98eb2c7cda6ef79c3f7709021b8f3471a0d5b3a3"),
    ("historical: add subscription answers", "e03c0c2509abe787a83c4958598ba4f45e255e85"),
    ("historical: clear v0.8 checksums", "ecc4ba75d7a8f942c1333daab79d54f42a3ab9c7"),
    ("historical: fix question search", "4fbdae6cafc6eb6f025d0c70415f789e6d0989d2"),
    ("historical: clear v0.7.1 checksums", "2a19b0b6915810740f69638c95578b9db2f518ed"),
    ("historical: remember profiles", "7ccb2d2c9437b4c6e9fa0034dd1b2afd856caa9f"),
    ("historical: clear v0.7 checksums", "fd683f82c217fc447b761234d3f465b413c26d20"),
    ("historical: fix rebuild proxy timeout", "1aad3870ac51c5345f86edbad38cc72c63f1ec23"),
    ("historical: clear v0.6.1 checksums", "5b1aabcaebdd0ae36bd2b2366ebe8b209ba51228"),
    ("historical: add profile menu", "b330c75325a9e469f061f4084f951973d8e16f81"),
    ("historical: record v0.6 scans", "b7f7bdc4251f42ca36e4d679b861130fdad624c4"),
    ("historical: repair source publishing", "0ee1d91ce5a4910aed311df8f99da6cb4fd0d624"),
    ("historical: clear v0.5.1 checksums", "645cc3025302876ad1b3061e824470b335a3e11a"),
    ("historical: release v0.5", "d4c4decee2587bb9689b180c3c10c10477e049e2"),
    ("historical: clear v0.5 checksums", "e37507b7e1ce38695488bbd1904589ffd9c13c27"),
    ("historical: add browser recovery", "e03a60b964385cb705ff4b577b14b3d537cfebfa"),
    ("historical: add multi-space wiki", "a5f9796c10b74c33199b1e87ab4e12846605f05b"),
    ("historical: close issue batch", "3350ee31bc251e36152fcd009a211eafdbc5b747"),
    ("historical: approve fingerprints", "f843f44260a6e80c47d27ad1f3cc1df490248acc"),
)

SYNTHETIC_CASES = (
    ("synthetic: operating doc modified", "M", "docs/deployment-automation.md", "mapped"),
    ("synthetic: profile doc added", "A", "docs/profile-menu.md", "mapped"),
    ("synthetic: design spec deleted", "D", "docs/superpowers/specs/2026-07-01-secret-scan-hook-design.md", "mapped"),
    ("synthetic: research doc modified", "M", "docs/superpowers/research/2026-07-01-tooling-advisory-memo.md", "mapped"),
    ("synthetic: comparison doc modified", "M", "docs/wiki-architecture-comparison/README.md", "mapped"),
    ("synthetic: Wiki article modified", "M", "wiki/agent.md", "full_rule"),
    ("synthetic: space index modified", "M", "spaces/civilization/index.md", "full_rule"),
    ("synthetic: workflow modified", "M", ".github/workflows/ci.yml", "full_rule"),
    ("synthetic: release note modified", "M", "docs/releases/v0.10.0.md", "full_rule"),
    ("synthetic: dispatcher modified", "M", "tools/run_verification_bundles.py", "full_rule"),
)


def git(repo: Path, *args: str) -> str:
    """Run Git and return stripped UTF-8 output for a test fixture."""
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def policy():
    """Parse the current policy through the unchanged published engine."""
    return SELECTOR.parse_policy((ROOT / ".transpara/verification.json").read_bytes())


def change(status: str, path: str):
    """Build one regular-file selector change with the requested status."""
    zero, old, new = "0" * 40, "a" * 40, "b" * 40
    if status == "A":
        return SELECTOR.Change("000000", "100644", zero, new, status, path)
    if status == "D":
        return SELECTOR.Change("100644", "000000", old, zero, status, path)
    return SELECTOR.Change("100644", "100644", old, new, status, path)


def owned_document(path: str) -> bool:
    """Return whether the fixed documentation checker owns this path."""
    return any(PurePosixPath(path).match(item) for item in CHECKER.DOCUMENT_PATTERNS)


class TempRepo:
    """Disposable exact-head repository for base-trust tests."""

    def __init__(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        git(self.root, "config", "user.name", "Verification Test")
        git(self.root, "config", "user.email", "verify@example.invalid")

    def cleanup(self) -> None:
        self.temporary.cleanup()

    def write(self, relative: str, content: bytes) -> None:
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def copy_adoption(self, policy_bytes: bytes | None = None) -> None:
        for relative in (*ADAPTER.ENGINE_PATHS, ADAPTER.MANIFEST_PATH):
            self.write(relative, (ROOT / relative).read_bytes())
        self.write(
            ADAPTER.POLICY_PATH,
            policy_bytes or (ROOT / ADAPTER.POLICY_PATH).read_bytes(),
        )

    def commit(self, message: str) -> str:
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", message)
        return git(self.root, "rev-parse", "HEAD")


class PolicyOwnershipTests(unittest.TestCase):
    """Prove complete ownership, conservative replay, and bundle coverage."""

    def test_policy_and_dispatcher_register_the_same_bundles(self) -> None:
        selected = policy()
        registry = RUNNER.bundle_commands(ROOT)
        self.assertEqual(set(selected.bundles), set(registry))
        self.assertEqual(selected.mandatory_bundles, RUNNER.MANDATORY_BUNDLES)

    def test_every_current_path_maps_or_explicitly_selects_full(self) -> None:
        selected = policy()
        paths = git(ROOT, "ls-files", "--cached", "--others", "--exclude-standard").splitlines()
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path):
                reason, bundles = SELECTOR.select_bundles(selected, [change("M", path)])
                self.assertIn(reason, {"mapped", "full_rule"})
                self.assertTrue(bundles)

    def test_unknown_future_domains_and_controls_fail_closed(self) -> None:
        selected = policy()
        cases = {
            "docs/tooling/new-unowned.md": "unmatched_path",
            "services/new-service/README.md": "unmatched_path",
            "deployments/new-profile/README.md": "unmatched_path",
            ".github/workflows/new.yml": "full_rule",
            "compile/new_service.py": "full_rule",
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                reason, bundles = SELECTOR.select_bundles(selected, [change("M", path)])
                self.assertEqual(reason, expected)
                self.assertEqual(bundles, selected.bundles)

    def test_replays_thirty_exact_historical_subjects(self) -> None:
        selected = policy()
        self.assertEqual(len(HISTORICAL_HEADS), 30)
        self.assertEqual(len({head for _, head in HISTORICAL_HEADS}), 30)
        for label, head in HISTORICAL_HEADS:
            with self.subTest(subject=label):
                base = git(ROOT, "rev-parse", f"{head}^")
                changes, _ = SELECTOR.raw_changes(str(ROOT), base, head, len(head))
                reason, bundles = SELECTOR.select_bundles(selected, changes)
                self.assertIn(reason, {"mapped", "full_rule", "unmatched_path"})
                self.assertTrue(bundles)
                if reason == "mapped":
                    self.assertTrue(all(owned_document(item.path) for item in changes))
                    self.assertEqual(bundles, ("mandatory-baseline", "repository-contracts"))
                else:
                    self.assertEqual(bundles, selected.bundles)

    def test_synthetic_cases_cover_each_bundle_at_least_five_times(self) -> None:
        selected = policy()
        coverage = {bundle: 0 for bundle in selected.bundles}
        for label, status, path, expected_reason in SYNTHETIC_CASES:
            with self.subTest(subject=label):
                reason, bundles = SELECTOR.select_bundles(selected, [change(status, path)])
                self.assertEqual(reason, expected_reason)
                expected = (
                    ("mandatory-baseline", "repository-contracts")
                    if expected_reason == "mapped"
                    else selected.bundles
                )
                self.assertEqual(bundles, expected)
                for bundle in bundles:
                    coverage[bundle] += 1
        self.assertTrue(all(count >= 5 for count in coverage.values()), coverage)

    def test_focused_registry_omits_every_expensive_runtime_suite(self) -> None:
        registry = RUNNER.bundle_commands(ROOT)
        rendered = [item for commands in registry.values() for command in commands for item in command.argv]
        joined = " ".join(rendered)
        for omitted in ("npm run build", "npm run test:py", "test_deployment.py", "test:browser", "test:shadow"):
            with self.subTest(command=omitted):
                self.assertNotIn(omitted, joined)
        self.assertIn("compile/secret_scan.py", rendered)

    def test_every_known_content_consumer_surface_selects_full(self) -> None:
        """Bind the repository's readers, generators, and route seeds to full."""
        selected = policy()
        consumers = {
            "static article input": "wiki/agent.md",
            "space navigation input": "spaces/civilization/index.md",
            "raw source input": "raw/inbox/manifest.jsonl",
            "release metadata": "docs/releases/v0.10.0.md",
            "route baseline seed": "docs/superpowers/plans/2026-09-05-multi-space-wiki-baseline-routes.txt",
            "root publication input": "index.md",
            "provenance input": "PROVENANCE.md",
            "embedded compile documentation": "compile/REBUILD.md",
            "terminology implementation": "compile/terminology_api.py",
            "navigation implementation": "compile/build_site.py",
        }
        for label, path in consumers.items():
            with self.subTest(consumer=label, path=path):
                reason, bundles = SELECTOR.select_bundles(
                    selected,
                    [change("M", path)],
                )
                self.assertEqual(reason, "full_rule")
                self.assertEqual(bundles, selected.bundles)


class AdapterTrustTests(unittest.TestCase):
    """Prove provenance, bootstrap fallback, policy control, and exact commits."""

    def make_repo(self) -> TempRepo:
        subject = TempRepo()
        self.addCleanup(subject.cleanup)
        return subject

    def test_vendored_bytes_match_exact_manifest_provenance(self) -> None:
        manifest = json.loads((ROOT / ADAPTER.MANIFEST_PATH).read_text())
        self.assertEqual(manifest["source_repository"], ADAPTER.ENGINE_SOURCE)
        self.assertEqual(manifest["source_commit"], ADAPTER.ENGINE_COMMIT)
        for entry in manifest["files"]:
            actual = hashlib.sha256((ROOT / entry["destination"]).read_bytes()).hexdigest()
            self.assertEqual(actual, entry["sha256"])

    def test_first_adoption_without_base_engine_can_only_select_full(self) -> None:
        subject = self.make_repo()
        subject.write("seed.txt", b"base\n")
        base = subject.commit("base without adoption")
        subject.copy_adoption()
        head = subject.commit("adopt verification")
        with tempfile.TemporaryDirectory() as target:
            plan = ADAPTER.build_plan(subject.root, "pull_request", base, head, "x/wiki", Path(target))
        self.assertEqual(plan["route"], "full")
        self.assertEqual(plan["reason"], "trusted_base_unavailable")

    def test_policy_change_on_head_selects_full_from_the_base(self) -> None:
        subject = self.make_repo()
        subject.copy_adoption()
        base = subject.commit("adopted base")
        policy_data = json.loads((ROOT / ADAPTER.POLICY_PATH).read_text())
        policy_data["rules"].append({"id": "candidate-only", "patterns": ["seed.txt"], "bundles": ["repository-contracts"]})
        subject.write(ADAPTER.POLICY_PATH, (json.dumps(policy_data) + "\n").encode())
        head = subject.commit("change policy")
        with tempfile.TemporaryDirectory() as target:
            plan = ADAPTER.build_plan(subject.root, "pull_request", base, head, "x/wiki", Path(target))
        self.assertEqual(plan["route"], "full")

    def test_attested_revisions_must_be_complete_object_ids(self) -> None:
        subject = self.make_repo()
        subject.copy_adoption()
        base = subject.commit("adopted base")
        subject.write("docs/profile-menu.md", b"# Example\n")
        head = subject.commit("documentation")
        with tempfile.TemporaryDirectory() as target:
            plan = ADAPTER.build_plan(subject.root, "pull_request", base[:12], head, "x/wiki", Path(target))
        self.assertEqual(plan["route"], "full")
        self.assertEqual(plan["reason"], "trusted_base_unavailable")

    def test_shadow_policy_never_executes_focused_bundles(self) -> None:
        selected = {key: None for key in RUNNER.PLAN_BINDINGS}
        selected.update(
            {
                "mode": "shadow",
                "route": "focused",
                "selected_bundles": ["mandatory-baseline", "repository-contracts"],
            }
        )
        with self.assertRaisesRegex(RUNNER.PlanError, "focused plan"):
            RUNNER.confirmed_bundles(selected, dict(selected), RUNNER.bundle_commands(ROOT))

    def test_candidate_python_startup_files_cannot_enter_trusted_routing(self) -> None:
        """Keep candidate imports outside the base scanner and plan pipeline."""
        subject = self.make_repo()
        subject.copy_adoption()
        subject.write(
            "tools/verification_adapter.py",
            (ROOT / "tools/verification_adapter.py").read_bytes(),
        )
        subject.write(
            "tools/run_verification_bundles.py",
            (ROOT / "tools/run_verification_bundles.py").read_bytes(),
        )
        subject.write(
            "compile/secret_scan.py",
            (ROOT / "compile/secret_scan.py").read_bytes(),
        )
        base = subject.commit("adopted base")
        attack = b"""\
import os
from pathlib import Path

Path(os.environ["ATTACK_MARKER"]).write_text("executed\\n", encoding="utf-8")
target = os.environ.get("ATTACK_TARGET")
if target:
    Path(target).write_text("candidate code replaced trusted bytes\\n", encoding="utf-8")
"""
        subject.write("json.py", attack)
        subject.write("sitecustomize.py", attack)
        head = subject.commit("add candidate import sentinels")

        with tempfile.TemporaryDirectory() as temporary:
            scratch = Path(temporary)
            adapter = scratch / "verification_adapter.py"
            dispatcher = scratch / "run_verification_bundles.py"
            scanner = scratch / "secret_scan_trusted.py"
            adapter.write_bytes(
                subprocess.check_output(
                    ["git", "-C", str(subject.root), "show", f"{base}:tools/verification_adapter.py"]
                )
            )
            dispatcher.write_bytes(
                subprocess.check_output(
                    ["git", "-C", str(subject.root), "show", f"{base}:tools/run_verification_bundles.py"]
                )
            )
            scanner.write_bytes(
                subprocess.check_output(
                    ["git", "-C", str(subject.root), "show", f"{base}:compile/secret_scan.py"]
                )
            )
            marker = scratch / "candidate-python-executed"
            environment = dict(os.environ)
            environment.update(
                {
                    "ATTACK_MARKER": str(marker),
                    "ATTACK_TARGET": str(scanner),
                }
            )
            # Prove the fixture can replace a trusted file when Python keeps
            # candidate startup paths. This negative control prevents a broken
            # attack fixture from making the isolated-path assertions vacuous.
            environment["PYTHONPATH"] = str(subject.root)
            control_target = scratch / "unisolated-target"
            control_target.write_text("trusted bytes\n", encoding="utf-8")
            environment["ATTACK_TARGET"] = str(control_target)
            subprocess.run(
                [sys.executable, "-c", "import json"],
                cwd=subject.root,
                env=environment,
                check=True,
            )
            self.assertEqual(
                control_target.read_text(encoding="utf-8"),
                "candidate code replaced trusted bytes\n",
            )
            self.assertTrue(marker.exists())
            marker.unlink()

            environment["ATTACK_TARGET"] = str(scanner)
            scanner_digest = hashlib.sha256(scanner.read_bytes()).hexdigest()
            subprocess.run(
                [sys.executable, "-I", str(scanner), "--changed-against", base],
                cwd=subject.root,
                env=environment,
                check=True,
            )
            self.assertEqual(hashlib.sha256(scanner.read_bytes()).hexdigest(), scanner_digest)
            self.assertFalse(marker.exists())

            environment["ATTACK_TARGET"] = str(dispatcher)
            dispatcher_digest = hashlib.sha256(dispatcher.read_bytes()).hexdigest()
            subprocess.run(
                [sys.executable, "-I", str(dispatcher), "--help"],
                cwd=subject.root,
                env=environment,
                check=True,
                capture_output=True,
            )
            self.assertEqual(hashlib.sha256(dispatcher.read_bytes()).hexdigest(), dispatcher_digest)
            self.assertFalse(marker.exists())

            trusted = scratch / "trusted"
            plan = scratch / "plan.json"
            environment["ATTACK_TARGET"] = str(adapter)
            adapter_digest = hashlib.sha256(adapter.read_bytes()).hexdigest()
            subprocess.run(
                [
                    sys.executable,
                    "-I",
                    str(adapter),
                    "--repo",
                    str(subject.root),
                    "--event",
                    "pull_request",
                    "--base",
                    base,
                    "--head",
                    head,
                    "--repository",
                    "x/wiki",
                    "--trusted-root",
                    str(trusted),
                    "--output",
                    str(plan),
                ],
                cwd=subject.root,
                env=environment,
                check=True,
            )
            self.assertEqual(hashlib.sha256(adapter.read_bytes()).hexdigest(), adapter_digest)
            self.assertFalse(marker.exists())

            plan_digest = hashlib.sha256(plan.read_bytes()).hexdigest()
            environment["ATTACK_TARGET"] = str(plan)
            parser = """\
import json
import re
import sys

value = json.load(open(sys.argv[1], encoding="utf-8"))
route = value.get("route")
reason = value.get("reason")
if route not in {"focused", "full"}:
    raise SystemExit("invalid route")
if not isinstance(reason, str) or re.fullmatch(r"[a-z0-9_-]+", reason) is None:
    raise SystemExit("invalid reason")
print(f"{route}\\t{reason}")
"""
            selected = subprocess.run(
                [sys.executable, "-I", "-", str(plan)],
                cwd=subject.root,
                env=environment,
                input=parser,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(selected.stdout, "full\tunmatched_path\n")
            self.assertEqual(hashlib.sha256(plan.read_bytes()).hexdigest(), plan_digest)
            self.assertFalse(marker.exists())


class WorkflowContractTests(unittest.TestCase):
    """Keep the required identity and both credential scans explicit."""

    def test_required_name_bootstrap_and_full_shadow_are_preserved(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("name: Build & Test", workflow)
        self.assertIn("trusted_base_adapter_unavailable", workflow)
        self.assertIn("full-shadow", workflow)
        self.assertIn("npm run test:py", workflow)

    def test_trusted_changed_range_scan_precedes_every_install(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        scan = workflow.index("--changed-against")
        self.assertIn("git show", workflow[:scan])
        self.assertLess(scan, workflow.index("pip install"))
        self.assertLess(scan, workflow.index("npm ci"))
        self.assertIn("--tree HEAD", workflow)

    def test_full_and_focused_routes_both_run_document_contract(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertGreaterEqual(workflow.count("tools/check_repository_contracts.py"), 2)
        runner = (ROOT / "tools/run_verification_bundles.py").read_text()
        self.assertIn("tools/check_repository_contracts.py", runner)

    def test_trusted_python_entry_points_are_isolated(self) -> None:
        """Prevent candidate root modules from entering trusted workflow code."""
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertEqual(workflow.count('python3 -I "$adapter"'), 2)
        self.assertIn('selection=$(python3 -I - "$plan"', workflow)
        self.assertEqual(workflow.count("secret_scan_trusted.py\" --changed-against"), 2)
        self.assertNotIn('python3 "$RUNNER_TEMP/secret_scan_trusted.py"', workflow)
        self.assertNotIn('python3 "${RUNNER_TEMP}/secret_scan_trusted.py"', workflow)
        self.assertIn('python3 -I "$RUNNER_TEMP/run_verification_bundles.py"', workflow)
        self.assertEqual(workflow.count("python3 -I - <<'PY'"), 2)
        self.assertNotIn('python3 "$adapter"', workflow)
        self.assertNotIn('selection=$(python3 - "$plan"', workflow)


if __name__ == "__main__":
    unittest.main()
