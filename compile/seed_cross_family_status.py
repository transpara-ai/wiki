#!/usr/bin/env python3
"""Seed / preserve the cross-family-adversarial-review commit status.

Invoked by .github/workflows/cross-family-review-status.yml on
pull_request_target events. The workflow runs a trusted BASE-branch copy of this
file and never checks out or executes PR-head code.

Why this is not an unconditional `POST pending`: a pull_request_target run can be
delayed minutes by GitHub Actions queue latency. A seed triggered by
`ready_for_review` that lands after the reviewer has already re-posted the
ready-state gate success would clobber that success -> pending (the PR #70
TOCTOU: OB marker wiki-pr70-gate-reclobber-restored-20260709T0624Z). But the seed
must still re-pend a *stale* success so the draft->ready transition forces a fresh
ready-state review. State alone cannot tell "fresh ready success" from "stale
draft success" — both are `success` on the same SHA. Time distinguishes them:
`decide()` PRESERVES only a terminal status provably newer than the triggering
event and re-pends everything else (fail-safe: re-pend blocks merge).
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys

CONTEXT = "cross-family-adversarial-review"
TERMINAL_STATES = frozenset({"success", "failure", "error"})


def _parse_ts(value: str | None) -> datetime.datetime | None:
    """Parse an ISO-8601 timestamp to an aware datetime, or None if unparseable.

    GitHub emits UTC "Z" timestamps (e.g. 2026-07-09T05:34:53Z). Normalize "Z" to
    an explicit offset and treat any naive result as UTC so comparisons never
    raise. Any parse failure returns None, which the caller treats as fail-safe.
    """
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed


def _belongs_to_pr(target_url: str | None, pr_url: str | None) -> bool:
    """True only when target_url links to pr_url's PR.

    Commit statuses are shared by SHA + context, so two PRs on the same head SHA
    share one status. The status target_url (set to the PR URL or a PR comment
    link by the gate/seed) is the per-PR discriminator: only a status that
    provably belongs to THIS PR may be preserved, so a fresh success posted for a
    different PR on the same SHA cannot satisfy this PR's gate. Fail closed when
    target_url is absent or points at a different PR. The separator check keeps
    /pull/72 from matching /pull/720.
    """
    if not isinstance(target_url, str) or not isinstance(pr_url, str):
        return False
    if not target_url or not pr_url:
        return False
    if target_url == pr_url:
        return True
    return any(target_url.startswith(pr_url + sep) for sep in ("#", "/", "?"))


def decide(current_state: str | None, current_updated_at: str | None,
           event_time: str | None, current_target_url: str | None,
           pr_url: str | None) -> str:
    """Return "preserve" (leave the status alone) or "pending" (POST pending).

    PRESERVE is the single, explicitly-proven permissive branch: it fires only
    when the current status is a terminal state AND belongs to this PR (its
    target_url) AND both timestamps parse AND the status is strictly newer than
    the triggering event. Every other input — no status, pending, a status for a
    different PR sharing the SHA, stale/equal timestamps, missing or malformed
    timestamps, or any unknown/future state value — falls through to "pending",
    which re-seeds a pending status and blocks merge (fail-closed).
    """
    if current_state not in TERMINAL_STATES:
        return "pending"
    if not _belongs_to_pr(current_target_url, pr_url):
        return "pending"
    current_dt = _parse_ts(current_updated_at)
    event_dt = _parse_ts(event_time)
    if current_dt is None or event_dt is None:
        return "pending"
    if current_dt > event_dt:
        return "preserve"
    return "pending"


def _run(command: list[str]) -> str:
    return subprocess.run(
        command, check=True, text=True, capture_output=True
    ).stdout


def current_context_status(
    github_repo: str, sha: str
) -> tuple[str, str | None, str | None]:
    """Return (state, updated_at, target_url) of the effective status for context.

    ("none", None, None) when no status for the context exists on the SHA. The
    combined /commits/{sha}/status endpoint already reduces to the latest status
    per context, so no history walk or pagination is needed.

    On any read error return the ("unreadable", None, None) sentinel: decide()
    maps it to "pending", so an unreadable state fails closed (re-pend / block)
    rather than leaving a possibly-stale success in place.
    """
    try:
        # per_page=100 so a commit with many status contexts cannot hide ours on a
        # later page (default 30) and get misread as "none" -> a clobbering re-pend.
        raw = _run(["gh", "api",
                    f"repos/{github_repo}/commits/{sha}/status?per_page=100"])
        statuses = json.loads(raw).get("statuses", [])
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as exc:
        print(f"warning: could not read current status ({exc}); failing closed "
              "to pending.", file=sys.stderr)
        return "unreadable", None, None
    for entry in statuses:
        if entry.get("context") == CONTEXT:
            return (str(entry.get("state") or "none"),
                    entry.get("updated_at"), entry.get("target_url"))
    return "none", None, None


def post_pending(github_repo: str, sha: str, pr_url: str, description: str) -> None:
    subprocess.run(
        [
            "gh", "api", "--method", "POST",
            f"repos/{github_repo}/statuses/{sha}",
            "-f", "state=pending",
            "-f", f"context={CONTEXT}",
            "-f", f"target_url={pr_url}",
            "-f", f"description={description}",
        ],
        check=True,
    )


def main() -> int:
    github_repo = os.environ["GH_REPO"]
    sha = os.environ["HEAD_SHA"]
    pr_url = os.environ.get("PR_URL", "")
    event_action = os.environ.get("EVENT_ACTION", "")
    event_time = os.environ.get("EVENT_TIME", "")

    description = "Waiting for exact-head cross-family adversarial review"
    if event_action == "ready_for_review":
        description = "Ready-state exact-head cross-family review required"

    state, updated_at, target_url = current_context_status(github_repo, sha)
    action = decide(state, updated_at, event_time, target_url, pr_url)
    if action == "preserve":
        print(
            f"preserve: {CONTEXT}={state} (target_url={target_url}) updated_at="
            f"{updated_at} is newer than event {event_time!r} and belongs to this "
            f"PR; leaving it intact."
        )
        return 0
    post_pending(github_repo, sha, pr_url, description)
    print(
        f"pending: seeded {CONTEXT}=pending on {sha} (prior state={state!r}, "
        f"updated_at={updated_at!r}, target_url={target_url!r}, event={event_time!r})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
