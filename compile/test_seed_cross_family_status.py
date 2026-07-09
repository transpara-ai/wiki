#!/usr/bin/env python3
"""Stdlib-assert tests for compile/seed_cross_family_status.py.

Run: python3 compile/test_seed_cross_family_status.py

The seed workflow re-pends the `cross-family-adversarial-review` commit status on
pull_request_target events. A delayed seed run must never clobber a *fresh* gate
success (the PR #70 TOCTOU), yet must still re-pend a *stale* success so the
draft->ready transition forces a fresh ready-state review. `decide()` is the pure
fail-safe kernel: PRESERVE only a terminal status provably newer than the
triggering event; re-pend (POST pending) on every other input — including no
status, pending, stale/equal timestamps, missing or malformed timestamps, and
any unknown/future state value.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import seed_cross_family_status as seed  # noqa: E402


# The PR #70 timeline (OB marker wiki-pr70-gate-reclobber-restored-20260709T0624Z):
EVENT = "2026-07-09T05:32:54Z"     # ready_for_review fired
FRESH = "2026-07-09T05:34:53Z"     # gate re-posted success AFTER the event
STALE = "2026-07-09T05:30:00Z"     # a draft-era success BEFORE the event


def test_no_status_seeds_pending():
    # No status exists yet -> establish presence.
    for absent in ("", "none", None):
        assert seed.decide(absent, None, EVENT) == "pending", absent
    print("ok test_no_status_seeds_pending")


def test_pending_status_stays_pending():
    # Idempotent: already pending -> pending (never accidentally "preserve").
    assert seed.decide("pending", FRESH, EVENT) == "pending"
    print("ok test_pending_status_stays_pending")


def test_fresh_success_is_preserved():
    # THE bug fix: a success posted after the event is a genuine response to it
    # and a delayed seed must NOT clobber it.
    assert seed.decide("success", FRESH, EVENT) == "preserve"
    print("ok test_fresh_success_is_preserved")


def test_stale_success_is_repended():
    # A success predating the event is stale (e.g. a draft-era review); the
    # draft->ready reset must force a fresh review, so re-pend.
    assert seed.decide("success", STALE, EVENT) == "pending"
    print("ok test_stale_success_is_repended")


def test_equal_timestamps_repend():
    # Ambiguous (same instant) -> fail-safe re-pend; PRESERVE needs strictly newer.
    assert seed.decide("success", EVENT, EVENT) == "pending"
    print("ok test_equal_timestamps_repend")


def test_fresh_failure_and_error_are_preserved():
    # Any fresh terminal status is honest information newer than the event;
    # don't overwrite a fresh explicit failure/error with a softer "pending".
    assert seed.decide("failure", FRESH, EVENT) == "preserve"
    assert seed.decide("error", FRESH, EVENT) == "preserve"
    print("ok test_fresh_failure_and_error_are_preserved")


def test_stale_failure_and_error_are_repended():
    assert seed.decide("failure", STALE, EVENT) == "pending"
    assert seed.decide("error", STALE, EVENT) == "pending"
    print("ok test_stale_failure_and_error_are_repended")


def test_missing_current_timestamp_repends():
    # Terminal state but we cannot prove it is newer -> fail-safe re-pend.
    for missing in (None, "", "   "):
        assert seed.decide("success", missing, EVENT) == "pending", missing
    print("ok test_missing_current_timestamp_repends")


def test_missing_event_timestamp_repends():
    # No event baseline to compare against -> cannot prove newer -> re-pend.
    for missing in (None, "", "   "):
        assert seed.decide("success", FRESH, missing) == "pending", missing
    print("ok test_missing_event_timestamp_repends")


def test_malformed_timestamps_repend():
    # Unparseable timestamps must never yield "preserve".
    assert seed.decide("success", "not-a-date", EVENT) == "pending"
    assert seed.decide("success", FRESH, "garbage") == "pending"
    assert seed.decide("success", "2026-13-99T99:99:99Z", EVENT) == "pending"
    print("ok test_malformed_timestamps_repend")


def test_unknown_or_future_state_repends():
    # Any state outside the terminal allowlist (incl. GitHub adding a new value)
    # must fail closed to pending, even with a newer timestamp.
    for unknown in ("queued", "neutral", "in_progress", "SUCCESS", "succeeded", "42"):
        assert seed.decide(unknown, FRESH, EVENT) == "pending", unknown
    print("ok test_unknown_or_future_state_repends")


def test_unreadable_status_sentinel_repends():
    # current_context_status() returns "unreadable" when the status read errors;
    # an unreadable state must never be trusted as fresh -> fail closed to pending.
    assert seed.decide("unreadable", FRESH, EVENT) == "pending"
    print("ok test_unreadable_status_sentinel_repends")


def test_timezone_offset_forms_compare_equivalently():
    # "Z" and "+00:00" denote the same instant; a success at ...53Z is newer than
    # an event expressed as ...54 minus a minute in explicit-offset form.
    assert seed.decide("success", "2026-07-09T05:34:53Z",
                       "2026-07-09T05:32:54+00:00") == "preserve"
    # And a genuinely older explicit-offset success is still re-pended.
    assert seed.decide("success", "2026-07-09T05:30:00+00:00",
                       "2026-07-09T05:32:54Z") == "pending"
    print("ok test_timezone_offset_forms_compare_equivalently")


def test_preserve_is_the_only_success_path_across_domain():
    # Sweep: PRESERVE fires IFF terminal state AND both timestamps parse AND
    # current strictly newer than event. Everything else -> pending.
    # "unreadable" is the sentinel current_context_status() returns on a read
    # error; like every other non-terminal value it must map to pending.
    states = ["", "none", "unreadable", "pending", "success", "failure", "error", "weird"]
    times = [None, "", "bad", STALE, EVENT, FRESH]
    terminal = {"success", "failure", "error"}
    for st in states:
        for cur in times:
            for evt in times:
                got = seed.decide(st, cur, evt)
                cur_dt = seed._parse_ts(cur)
                evt_dt = seed._parse_ts(evt)
                expect_preserve = (
                    st in terminal
                    and cur_dt is not None
                    and evt_dt is not None
                    and cur_dt > evt_dt
                )
                want = "preserve" if expect_preserve else "pending"
                assert got == want, (st, cur, evt, got, want)
    print("ok test_preserve_is_the_only_success_path_across_domain")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d seed-status tests passed" % len(fns))
