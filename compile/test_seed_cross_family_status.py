#!/usr/bin/env python3
"""Stdlib-assert tests for compile/seed_cross_family_status.py.

Run: python3 compile/test_seed_cross_family_status.py

The seed workflow re-pends the `cross-family-adversarial-review` commit status on
pull_request_target events. A delayed seed run must never clobber a *fresh* gate
success (the PR #70 TOCTOU), yet must still re-pend a *stale* success so the
draft->ready transition forces a fresh ready-state review. `decide()` is the pure
fail-safe kernel: PRESERVE only a terminal status that both is provably newer than
the triggering event AND (because statuses are shared by SHA+context across PRs)
provably belongs to this PR via its target_url; re-pend on every other input.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import seed_cross_family_status as seed  # noqa: E402


# The PR #70 timeline (OB marker wiki-pr70-gate-reclobber-restored-20260709T0624Z):
EVENT = "2026-07-09T05:32:54Z"     # ready_for_review fired
FRESH = "2026-07-09T05:34:53Z"     # gate re-posted success AFTER the event
STALE = "2026-07-09T05:30:00Z"     # a draft-era success BEFORE the event

PR_URL = "https://github.com/transpara-ai/wiki/pull/72"
OTHER_PR = "https://github.com/transpara-ai/wiki/pull/99"


def _decide(state, cur, evt, target_url=PR_URL, pr_url=PR_URL):
    """decide() with a target_url that belongs to this PR by default."""
    return seed.decide(state, cur, evt, target_url, pr_url)


def test_no_status_seeds_pending():
    for absent in ("", "none", None):
        assert _decide(absent, None, EVENT) == "pending", absent
    print("ok test_no_status_seeds_pending")


def test_pending_status_stays_pending():
    assert _decide("pending", FRESH, EVENT) == "pending"
    print("ok test_pending_status_stays_pending")


def test_fresh_success_is_preserved():
    # THE bug fix: a success posted after the event, for this PR, is a genuine
    # response and a delayed seed must NOT clobber it.
    assert _decide("success", FRESH, EVENT) == "preserve"
    print("ok test_fresh_success_is_preserved")


def test_stale_success_is_repended():
    assert _decide("success", STALE, EVENT) == "pending"
    print("ok test_stale_success_is_repended")


def test_equal_timestamps_repend():
    assert _decide("success", EVENT, EVENT) == "pending"
    print("ok test_equal_timestamps_repend")


def test_fresh_failure_and_error_are_preserved():
    assert _decide("failure", FRESH, EVENT) == "preserve"
    assert _decide("error", FRESH, EVENT) == "preserve"
    print("ok test_fresh_failure_and_error_are_preserved")


def test_stale_failure_and_error_are_repended():
    assert _decide("failure", STALE, EVENT) == "pending"
    assert _decide("error", STALE, EVENT) == "pending"
    print("ok test_stale_failure_and_error_are_repended")


def test_missing_current_timestamp_repends():
    for missing in (None, "", "   "):
        assert _decide("success", missing, EVENT) == "pending", missing
    print("ok test_missing_current_timestamp_repends")


def test_missing_event_timestamp_repends():
    for missing in (None, "", "   "):
        assert _decide("success", FRESH, missing) == "pending", missing
    print("ok test_missing_event_timestamp_repends")


def test_malformed_timestamps_repend():
    assert _decide("success", "not-a-date", EVENT) == "pending"
    assert _decide("success", FRESH, "garbage") == "pending"
    assert _decide("success", "2026-13-99T99:99:99Z", EVENT) == "pending"
    print("ok test_malformed_timestamps_repend")


def test_unknown_or_future_state_repends():
    for unknown in ("queued", "neutral", "in_progress", "SUCCESS", "succeeded", "42"):
        assert _decide(unknown, FRESH, EVENT) == "pending", unknown
    print("ok test_unknown_or_future_state_repends")


def test_unreadable_status_sentinel_repends():
    assert _decide("unreadable", FRESH, EVENT) == "pending"
    print("ok test_unreadable_status_sentinel_repends")


def test_fresh_success_for_another_pr_is_repended():
    # Shared head SHA: statuses are keyed by SHA+context, so a fresh success whose
    # target_url points at a DIFFERENT PR must NOT satisfy this PR's gate.
    assert seed.decide("success", FRESH, EVENT, OTHER_PR, PR_URL) == "pending"
    assert seed.decide("success", FRESH, EVENT, OTHER_PR + "#issuecomment-1", PR_URL) == "pending"
    print("ok test_fresh_success_for_another_pr_is_repended")


def test_fresh_success_for_this_pr_comment_url_is_preserved():
    # The gate posts target_url as a PR comment link; it still belongs to this PR.
    assert seed.decide("success", FRESH, EVENT, PR_URL + "#issuecomment-2", PR_URL) == "preserve"
    assert seed.decide("success", FRESH, EVENT, PR_URL + "/files", PR_URL) == "preserve"
    print("ok test_fresh_success_for_this_pr_comment_url_is_preserved")


def test_missing_target_url_is_repended():
    for missing in (None, "", "   "):
        assert seed.decide("success", FRESH, EVENT, missing, PR_URL) == "pending", missing
    print("ok test_missing_target_url_is_repended")


def test_pr_number_prefix_is_not_confused():
    # pull/72 must not match pull/720 (string-prefix without a boundary).
    assert seed.decide("success", FRESH, EVENT,
                       "https://github.com/transpara-ai/wiki/pull/720", PR_URL) == "pending"
    print("ok test_pr_number_prefix_is_not_confused")


def test_preserve_is_the_only_success_path_across_domain():
    # Sweep: PRESERVE fires IFF terminal state AND both timestamps parse AND
    # current strictly newer than event AND target_url belongs to this PR.
    states = ["", "none", "unreadable", "pending", "success", "failure", "error", "weird"]
    times = [None, "", "bad", STALE, EVENT, FRESH]
    urls = [PR_URL, PR_URL + "#c", PR_URL + "/files", OTHER_PR, "", None]
    terminal = {"success", "failure", "error"}
    for st in states:
        for cur in times:
            for evt in times:
                for turl in urls:
                    got = seed.decide(st, cur, evt, turl, PR_URL)
                    cur_dt = seed._parse_ts(cur)
                    evt_dt = seed._parse_ts(evt)
                    expect_preserve = (
                        st in terminal
                        and cur_dt is not None
                        and evt_dt is not None
                        and cur_dt > evt_dt
                        and seed._belongs_to_pr(turl, PR_URL)
                    )
                    want = "preserve" if expect_preserve else "pending"
                    assert got == want, (st, cur, evt, turl, got, want)
    print("ok test_preserve_is_the_only_success_path_across_domain")


def test_timezone_offset_forms_compare_equivalently():
    assert seed.decide("success", "2026-07-09T05:34:53Z",
                       "2026-07-09T05:32:54+00:00", PR_URL, PR_URL) == "preserve"
    assert seed.decide("success", "2026-07-09T05:30:00+00:00",
                       "2026-07-09T05:32:54Z", PR_URL, PR_URL) == "pending"
    print("ok test_timezone_offset_forms_compare_equivalently")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d seed-status tests passed" % len(fns))
