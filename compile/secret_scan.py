#!/usr/bin/env python3
"""Fail-closed secret scanner for the wiki repo (stdlib only, air-gap native).

Design packet: docs/superpowers/specs/2026-07-01-secret-scan-hook-design.md.
Modes:
  --staged                  scan the staged index (pre-commit hook surface)
  --changed-against <base>  scan every (path, blob) occurrence introduced by
                            any commit in merge-base(<base>, HEAD)..HEAD (CI)
  --tree <rev>              scan every blob occurrence in a full tree (evidence)

Outcome vocabulary is closed: every occurrence resolves to pass, allowlisted,
or block. There is no skip outcome. Anything the scanner cannot positively
scan — unresolvable base, unreadable blob, gitlink, .gitmodules change,
invalid allowlist, timeout, any git error — blocks. Findings are reported by
rule/path/offset/hash only; matched secret bytes are never printed.
"""
import argparse
import datetime
import hashlib
import json
import math
import pathlib
import re
import signal
import subprocess
import sys
from dataclasses import dataclass

MAX_BLOB_BYTES = 1024 * 1024
MAX_VALIDITY_DAYS = 180
ZERO_SHA_RE = re.compile(r"^0+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GITLINK_MODE = "160000"

# --- detector contract (§3.2 of the design packet; the fenced block is law) --

PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY( BLOCK)?-----")
AWS_RE = re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")
GITHUB_RES = (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,255}\b"),
              re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,255}\b"))
SLACK_RE = re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")
OPENAI_RE = re.compile(r"\bsk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_-]{20,}\b")
GCP_TYPE_RE = re.compile(r'"type"\s*:\s*"service_account"')
GCP_KEY_RE = re.compile(r'"private_key"\s*:\s*"')
JWT_RE = re.compile(
    r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")
ASSIGN_PREFIX_RE = re.compile(
    r"(?i)\b(?:api[_-]?key|secret|token|passwd|password)\b\s*[:=]\s*[\"']?")
CANDIDATE_RE = re.compile(r"[A-Za-z0-9+/=_-]{16,}")
ENTROPY_TOKEN_RE = re.compile(r"[A-Za-z0-9+/=_-]{32,}")
ASSIGN_MIN_ENTROPY = 3.5
BACKSTOP_MIN_ENTROPY = 4.5
BACKSTOP_MIN_LEN = 32
PLACEHOLDERS = {"changeme", "example"}

RULE_IDS = (
    "private-key", "aws-access-key-id", "github-token", "slack-token",
    "openai-sk-key", "gcp-sa-json", "jwt", "generic-assignment",
    "high-entropy",
)


class ScanError(Exception):
    """Any condition that must fail closed."""


@dataclass
class Finding:
    rule_id: str
    start: int          # character offset in scan_text
    end: int
    byte_offset: int    # utf-8 byte offset (§3.1.1 span convention)
    match_sha256: str


@dataclass
class Outcome:
    path: str
    outcome: str        # pass | allowlisted | block
    clearable: bool
    reason: str
    findings: tuple = ()


class Allowlist:
    def __init__(self, fingerprints, blob_reviews):
        self.fingerprints = set(fingerprints)
        self.blob_reviews = set(blob_reviews)


def shannon_entropy(token):
    if not token:
        return 0.0
    counts = {}
    for ch in token:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(token)
    return -sum(c / n * math.log2(c / n) for c in counts.values())


def _mk_finding(rule_id, text, start, end):
    span = text[start:end]
    return Finding(
        rule_id=rule_id, start=start, end=end,
        byte_offset=len(text[:start].encode("utf-8")),
        match_sha256=hashlib.sha256(span.encode("utf-8")).hexdigest())


def scan_text(text):
    """Run every §3.2 detector over decoded text; return all findings."""
    findings = []
    for regex in (PRIVATE_KEY_RE,):
        for m in regex.finditer(text):
            findings.append(_mk_finding("private-key", text, *m.span()))
    for m in AWS_RE.finditer(text):
        findings.append(_mk_finding("aws-access-key-id", text, *m.span()))
    for regex in GITHUB_RES:
        for m in regex.finditer(text):
            findings.append(_mk_finding("github-token", text, *m.span()))
    for m in SLACK_RE.finditer(text):
        findings.append(_mk_finding("slack-token", text, *m.span()))
    for m in OPENAI_RE.finditer(text):
        findings.append(_mk_finding("openai-sk-key", text, *m.span()))
    if GCP_TYPE_RE.search(text):
        m = GCP_KEY_RE.search(text)
        if m:
            findings.append(_mk_finding("gcp-sa-json", text, *m.span()))
    for m in JWT_RE.finditer(text):
        findings.append(_mk_finding("jwt", text, *m.span()))
    for m in ASSIGN_PREFIX_RE.finditer(text):
        cand = CANDIDATE_RE.match(text, m.end())
        if not cand:
            continue
        tok = cand.group()
        if tok.lower() in PLACEHOLDERS or set(tok.lower()) == {"x"}:
            continue
        if shannon_entropy(tok) >= ASSIGN_MIN_ENTROPY:
            findings.append(
                _mk_finding("generic-assignment", text, *cand.span()))
    taken = [(f.start, f.end) for f in findings]
    for m in ENTROPY_TOKEN_RE.finditer(text):
        s, e = m.span()
        if e - s < BACKSTOP_MIN_LEN:
            continue
        if any(s < te and ts < e for ts, te in taken):
            continue  # already matched by a rule above (§3.2)
        if shannon_entropy(m.group()) >= BACKSTOP_MIN_ENTROPY:
            findings.append(_mk_finding("high-entropy", text, s, e))
    return findings


# ------------------------------------------------------------ git plumbing

def git(root, *args, binary=False):
    try:
        proc = subprocess.run(["git"] + list(args), cwd=str(root),
                              capture_output=True)
    except Exception as exc:  # missing git, empty PATH, OS error — block
        raise ScanError("git unavailable: %s" % exc)
    if proc.returncode != 0:
        raise ScanError("git %s failed: %s"
                        % (args[0], proc.stderr.decode("utf-8", "replace").strip()))
    return proc.stdout if binary else proc.stdout.decode("utf-8", "strict")


def repo_root(cwd):
    return pathlib.Path(git(cwd, "rev-parse", "--show-toplevel").strip())


def read_blob(root, oid):
    return git(root, "cat-file", "blob", oid, binary=True)


def _decode_path(raw):
    try:
        return raw.decode("utf-8", "strict")
    except UnicodeDecodeError:
        raise ScanError("path is not valid UTF-8 — fail closed: %r" % raw)


def parse_raw_records(payload):
    """Parse `git diff --raw -z` output into (new_mode, new_oid, status, path)."""
    records = []
    fields = payload.split(b"\0")
    i = 0
    while i < len(fields):
        meta = fields[i]
        if not meta:
            i += 1
            continue
        if not meta.startswith(b":"):
            raise ScanError("unparseable raw record — fail closed: %r" % meta)
        parts = meta[1:].decode("utf-8", "strict").split(" ")
        if len(parts) != 5:
            raise ScanError("unparseable raw record — fail closed: %r" % meta)
        _old_mode, new_mode, _old_oid, new_oid, status = parts
        if i + 1 >= len(fields):
            raise ScanError("raw record missing path — fail closed")
        path = _decode_path(fields[i + 1])
        records.append((new_mode, new_oid, status, path))
        i += 2
    return records


def occurrences_from_records(records):
    """Map raw records to scan occurrences; hard-block non-scannable entries."""
    blocks, occs = [], []
    for new_mode, new_oid, status, path in records:
        name = path.rsplit("/", 1)[-1]
        if name == ".gitmodules":
            blocks.append(Outcome(path, "block", False,
                                  ".gitmodules change — submodules are not "
                                  "permitted in the scan domain"))
            continue
        if new_mode == GITLINK_MODE:
            blocks.append(Outcome(path, "block", False,
                                  "gitlink (mode 160000) — submodule content "
                                  "is not scannable"))
            continue
        if status == "D":
            continue  # a deletion introduces no content (domain, not outcome)
        if ZERO_SHA_RE.match(new_oid):
            blocks.append(Outcome(path, "block", False,
                                  "unresolvable staged object — fail closed"))
            continue
        occs.append((path, new_oid))
    return blocks, occs


def enumerate_staged(root):
    payload = git(root, "diff", "--cached", "--raw", "--no-renames", "-z",
                  binary=True)
    return occurrences_from_records(parse_raw_records(payload))


def enumerate_changed_against(root, base):
    if ZERO_SHA_RE.match(base.strip() or "0"):
        raise ScanError("base ref is all-zeros/empty — fail closed")
    git(root, "rev-parse", "--verify", "--quiet", base + "^{commit}")
    merge_base = git(root, "merge-base", base, "HEAD").strip()
    commits = git(root, "rev-list", merge_base + "..HEAD").split()
    blocks, occs = [], []
    for commit in commits:
        payload = git(root, "diff-tree", "-r", "-m", "--no-renames",
                      "--no-commit-id", "--raw", "-z", commit, binary=True)
        b, o = occurrences_from_records(parse_raw_records(payload))
        blocks.extend(b)
        occs.extend(o)
    seen, unique = set(), []
    for occ in occs:
        if occ not in seen:  # dedup is an optimization only (§3, CFADA-r3 B3)
            seen.add(occ)
            unique.append(occ)
    return blocks, unique


def enumerate_tree(root, rev):
    payload = git(root, "ls-tree", "-r", "-z", rev, binary=True)
    blocks, occs = [], []
    for field in payload.split(b"\0"):
        if not field:
            continue
        meta, _, raw_path = field.partition(b"\t")
        mode, _objtype, oid = meta.decode("utf-8", "strict").split(" ")
        path = _decode_path(raw_path)
        if path.rsplit("/", 1)[-1] == ".gitmodules":
            blocks.append(Outcome(path, "block", False,
                                  ".gitmodules present — submodules are not "
                                  "permitted in the scan domain"))
            continue
        if mode == GITLINK_MODE:
            blocks.append(Outcome(path, "block", False,
                                  "gitlink (mode 160000) — not scannable"))
            continue
        occs.append((path, oid))
    return blocks, occs


# --------------------------------------------------------------- allowlist

FP_KEYS = {"type", "rule_id", "canonical_path", "blob_sha256", "match_sha256",
           "byte_offset", "reason", "owner", "reviewed_by", "reviewed_on",
           "expires_on"}
BR_KEYS = {"type", "canonical_path", "blob_sha256", "reason", "owner",
           "reviewed_by", "reviewed_on", "expires_on"}


def _validate_dates(entry, lineno):
    try:
        reviewed = datetime.date.fromisoformat(entry["reviewed_on"])
        expires = datetime.date.fromisoformat(entry["expires_on"])
    except (ValueError, TypeError):
        raise ScanError("allowlist line %d: bad ISO date" % lineno)
    today = datetime.date.today()
    if expires < today:
        raise ScanError("allowlist line %d: entry expired %s"
                        % (lineno, entry["expires_on"]))
    if (expires - reviewed).days > MAX_VALIDITY_DAYS:
        raise ScanError("allowlist line %d: validity exceeds %d days"
                        % (lineno, MAX_VALIDITY_DAYS))


def _require_str(entry, keys, lineno):
    for key in keys:
        value = entry.get(key)
        if not isinstance(value, str) or not value:
            raise ScanError("allowlist line %d: %r must be a non-empty string"
                            % (lineno, key))


def load_allowlist(path):
    if not path.exists():
        return Allowlist([], [])
    fingerprints, blob_reviews = [], []
    for lineno, line in enumerate(path.read_text("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            raise ScanError("allowlist line %d: not valid JSON" % lineno)
        if not isinstance(entry, dict):
            raise ScanError("allowlist line %d: not an object" % lineno)
        etype = entry.get("type")
        if etype == "fingerprint":
            if set(entry) != FP_KEYS:
                raise ScanError("allowlist line %d: fingerprint keys must be "
                                "exactly %s" % (lineno, sorted(FP_KEYS)))
            _require_str(entry, FP_KEYS - {"byte_offset"}, lineno)
            if entry["rule_id"] not in RULE_IDS:
                raise ScanError("allowlist line %d: unknown rule_id %r"
                                % (lineno, entry["rule_id"]))
            offset = entry["byte_offset"]
            if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
                raise ScanError("allowlist line %d: byte_offset must be a "
                                "non-negative integer" % lineno)
            for key in ("blob_sha256", "match_sha256"):
                if not SHA256_RE.match(entry[key]):
                    raise ScanError("allowlist line %d: %s is not hex sha256"
                                    % (lineno, key))
            _validate_dates(entry, lineno)
            identity = (entry["rule_id"], entry["canonical_path"],
                        entry["blob_sha256"], entry["match_sha256"], offset)
            if identity in fingerprints:
                raise ScanError("allowlist line %d: duplicate identity" % lineno)
            fingerprints.append(identity)
        elif etype == "blob_review":
            if set(entry) != BR_KEYS:
                raise ScanError("allowlist line %d: blob_review keys must be "
                                "exactly %s" % (lineno, sorted(BR_KEYS)))
            _require_str(entry, BR_KEYS, lineno)
            if not SHA256_RE.match(entry["blob_sha256"]):
                raise ScanError("allowlist line %d: blob_sha256 is not hex "
                                "sha256" % lineno)
            _validate_dates(entry, lineno)
            identity = (entry["canonical_path"], entry["blob_sha256"])
            if identity in blob_reviews:
                raise ScanError("allowlist line %d: duplicate identity" % lineno)
            blob_reviews.append(identity)
        else:
            raise ScanError("allowlist line %d: unknown type %r — fail closed"
                            % (lineno, etype))
    return Allowlist(fingerprints, blob_reviews)


# ------------------------------------------------------------ occurrence

def scan_occurrence(root, path, oid, allowlist):
    """Classify one (path, blob) occurrence per the §3.1 input-class table."""
    try:
        blob = read_blob(root, oid)
    except ScanError as exc:
        return Outcome(path, "block", False,
                       "unreadable blob — non-clearable (%s)" % exc)
    blob_sha256 = hashlib.sha256(blob).hexdigest()
    reviewed = (path, blob_sha256) in allowlist.blob_reviews
    if len(blob) > MAX_BLOB_BYTES:
        if reviewed:
            return Outcome(path, "allowlisted", True,
                           "oversized blob cleared by blob_review")
        return Outcome(path, "block", True,
                       "oversized (> 1 MiB) — too large to scan; review "
                       "manually and attest with a blob_review entry")
    if b"\x00" in blob:
        advisory = scan_text(blob.decode("utf-8", "replace"))
        if reviewed:
            return Outcome(path, "allowlisted", True,
                           "binary blob cleared by blob_review")
        note = ("; advisory: pattern scan reports %d finding(s) inside"
                % len(advisory)) if advisory else ""
        return Outcome(path, "block", True,
                       "binary content cannot be text-scanned — review "
                       "manually and attest with a blob_review entry" + note)
    # scannable text: blob_review is rejected for this class by construction
    findings = scan_text(blob.decode("utf-8", "replace"))
    blocked = tuple(
        f for f in findings
        if (f.rule_id, path, blob_sha256, f.match_sha256, f.byte_offset)
        not in allowlist.fingerprints)
    if blocked:
        return Outcome(path, "block", True,
                       "%d uncleared finding(s)" % len(blocked), blocked)
    if findings:
        return Outcome(path, "allowlisted", True,
                       "all findings cleared by fingerprints", tuple(findings))
    return Outcome(path, "pass", False, "scanned clean")


# ------------------------------------------------------------------ report

def report(outcomes, out=sys.stdout):
    blocked = [o for o in outcomes if o.outcome == "block"]
    for o in blocked:
        print("BLOCK %s — %s" % (o.path, o.reason), file=out)
        for f in o.findings:
            print("  finding rule=%s byte_offset=%d match_sha256=%s"
                  % (f.rule_id, f.byte_offset, f.match_sha256), file=out)
    counts = {}
    for o in outcomes:
        counts[o.outcome] = counts.get(o.outcome, 0) + 1
    print("secret-scan: %d occurrence(s): %s"
          % (len(outcomes),
             ", ".join("%d %s" % (v, k) for k, v in sorted(counts.items()))),
          file=out)
    return len(blocked)


def run(mode_args):
    root = repo_root(pathlib.Path.cwd())
    allowlist = load_allowlist(root / "compile" / ".secretsallow")
    if mode_args.staged:
        blocks, occs = enumerate_staged(root)
    elif mode_args.changed_against is not None:
        blocks, occs = enumerate_changed_against(root, mode_args.changed_against)
    else:
        blocks, occs = enumerate_tree(root, mode_args.tree)
    outcomes = list(blocks)
    for path, oid in occs:
        outcomes.append(scan_occurrence(root, path, oid, allowlist))
    return report(outcomes)


class _Timeout(Exception):
    pass


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--staged", action="store_true")
    group.add_argument("--changed-against", metavar="BASE")
    group.add_argument("--tree", metavar="REV")
    parser.add_argument("--max-seconds", type=float, default=None,
                        help="in-process bound; expiry fails closed")
    args = parser.parse_args(argv)
    if args.max_seconds is not None:
        def _alarm(_sig, _frame):
            raise _Timeout()
        signal.signal(signal.SIGALRM, _alarm)
        signal.setitimer(signal.ITIMER_REAL, args.max_seconds)
    try:
        blocked = run(args)
    except _Timeout:
        print("secret-scan: BLOCK — timeout (scan did not finish in %.6gs; "
              "fail closed)" % args.max_seconds, file=sys.stderr)
        return 1
    except ScanError as exc:
        print("secret-scan: BLOCK — %s" % exc, file=sys.stderr)
        return 1
    except Exception as exc:  # anything unexpected fails closed
        print("secret-scan: BLOCK — internal error (%r); fail closed" % exc,
              file=sys.stderr)
        return 1
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
