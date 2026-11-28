# test_smoke.py - Smoke tests (plain asserts, no test framework)
import datetime

from store import CaseRegistry, generate_demo_data, followups, registry, new_case_id
from rules import build_rules, explain
from scheduler import SlotFinder, get_missed, auto_reschedule, booked, schedule_followup


def test_registry_rejects_invalid_severity():
    """Registry rejects an invalid severity."""
    reg = CaseRegistry()
    try:
        reg["X1"] = {
            "name": "Test", "age": 20, "sport": "cricket",
            "injury": "fracture", "severity": "INVALID", "physio": "Dr. Meera",
        }
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "severity" in str(e).lower() or "Unknown" in str(e)
    print("  PASS: Registry rejects invalid severity")


def test_explain_severity_rule():
    """explain() reports 'severity rule' for a severe kabaddi case."""
    generate_demo_data()
    # Create a known severe kabaddi case
    from store import new_case_id
    cid = new_case_id()
    registry[cid] = {
        "name": "TestPlayer", "age": 25, "sport": "kabaddi",
        "injury": "ACL tear", "severity": "severe", "physio": "Dr. Deep Raj",
    }
    rules = build_rules(cid)
    layer, value, overridden = explain(rules, "interval_days")
    assert layer == "severity rule", f"Expected 'severity rule', got '{layer}'"
    assert value == 2, f"Expected 2, got {value}"
    print("  PASS: explain() reports severity rule for severe kabaddi case")


def test_slotfinder_no_sundays_and_stops():
    """SlotFinder yields no Sundays and stops at the limit."""
    # Pick a Monday
    start = datetime.date(2026, 11, 23)  # Monday
    finder = SlotFinder(start, max_days=14)
    dates = []
    for d in finder:
        dates.append(d)
    for d in dates:
        assert d.weekday() != 6, f"Sunday found: {d}"
    # Should stop (StopIteration is implicit in for-loop)
    it = SlotFinder(start, max_days=3)
    count = 0
    try:
        while True:
            next(it)
            count = count + 1
    except StopIteration:
        pass
    assert count > 0, "SlotFinder yielded nothing"
    assert count <= 4, f"SlotFinder yielded too many: {count}"
    print("  PASS: SlotFinder skips Sundays and raises StopIteration")


def test_auto_reschedule_clears_missed():
    """After generate_demo_data and auto_reschedule: get_missed() is empty."""
    generate_demo_data()
    missed_before = get_missed()
    assert len(missed_before) >= 3, f"Expected >=3 missed, got {len(missed_before)}"
    auto_reschedule()
    missed_after = get_missed()
    assert len(missed_after) == 0, f"Expected 0 missed after reschedule, got {len(missed_after)}"
    print("  PASS: auto_reschedule clears all missed follow-ups")


def test_max_per_day_not_exceeded():
    """No day exceeds max_per_day pending follow-ups."""
    generate_demo_data()
    auto_reschedule()
    day_counts = booked()
    for day, count in day_counts.items():
        assert count <= 3, f"Day {day} has {count} bookings (max 3)"
    print("  PASS: No day exceeds max_per_day")


def test_v1_1_spec_requirements():
    """Spec v1.1 checks: no duplicates, max 3, 2 due today, and severe triage order."""
    generate_demo_data()

    # a. after generate_demo_data(): no case has two pending on one date, max 3 per date
    pending_case_dates = [(f.case_id, f.due) for f in followups if f.status == "pending"]
    assert len(pending_case_dates) == len(set(pending_case_dates)), "Case has multiple pending follow-ups on same date"
    for day, count in booked().items():
        assert count <= 3, f"Date {day} has {count} pending bookings (max 3)"

    # b. after generate_demo_data(): at least 2 follow-ups due today
    today = datetime.date.today()
    due_today = [f for f in followups if f.due == today and f.status == "pending"]
    assert len(due_today) >= 2, f"Expected >= 2 follow-ups due today, got {len(due_today)}"

    # Check at least 5 missed with at least 2 physios
    missed_before = get_missed()
    assert len(missed_before) >= 5, f"Expected >= 5 missed, got {len(missed_before)}"
    assert len({f.physio for f in missed_before}) >= 2, "Expected >= 2 different physios among missed"

    # d. triage: if any severe case was missed, the first rebooked follow-up belongs to a severe case
    has_severe = any([registry[f.case_id]["severity"] == "severe" for f in missed_before])

    explanations = auto_reschedule()

    # c. after auto_reschedule(): get_missed() is empty and the checks in (a) still hold
    assert len(get_missed()) == 0, "Missed follow-ups remain after auto_reschedule"
    pending_case_dates_after = [(f.case_id, f.due) for f in followups if f.status == "pending"]
    assert len(pending_case_dates_after) == len(set(pending_case_dates_after)), "Case has duplicate pending after reschedule"
    for day, count in booked().items():
        assert count <= 3, f"Date {day} has {count} pending bookings after reschedule (max 3)"

    if has_severe:
        assert len(explanations) > 0, "Expected reschedule explanations"
        first_line = explanations[0].split("\n")[0]
        assert "SEVERE" in first_line, f"Expected first rebooked follow-up to be SEVERE, got: {first_line}"

    print("  PASS: Spec v1.1 data realism, today's queue, and triage tests")


def test_v1_2_spec_requirements():
    """Spec v1.2 checks: rebooked count equals added count, and scheduling a new case returns FollowUp."""
    # a. after generate_demo_data(), record len(followups); after auto_reschedule(), the number of
    # follow-ups with status "rebooked" equals the number of follow-ups added.
    generate_demo_data()
    initial_count = len(followups)
    auto_reschedule()
    rebooked_count = len([f for f in followups if f.status == "rebooked"])
    added_count = len(followups) - initial_count
    assert rebooked_count == added_count, f"Rebooked ({rebooked_count}) != added ({added_count})"

    # b. add a valid case to registry using new_case_id(); schedule_followup(that_id) returns a
    # (FollowUp, explanation) tuple whose first item is not None.
    cid = new_case_id()
    registry[cid] = {
        "name": "NewPlayer", "age": 21, "sport": "cricket",
        "injury": "hamstring strain", "severity": "mild", "physio": "Dr. Deep Raj",
    }
    result = schedule_followup(cid)
    assert isinstance(result, tuple) and len(result) == 2, f"Expected 2-tuple, got {result}"
    fu, explanation = result
    assert fu is not None, f"Expected FollowUp object, got None: {explanation}"
    print("  PASS: Spec v1.2 rebooked count matches added, and new case scheduled successfully")


def test_severe_cases_assigned_to_dr_deep_raj():
    """All severe cases and their scheduled follow-ups are assigned to Dr. Deep Raj."""
    generate_demo_data()
    for cid, case in registry.items():
        if case["severity"] == "severe":
            assert case["physio"] == "Dr. Deep Raj", f"Severe case {cid} assigned to {case['physio']}"
    auto_reschedule()
    for f in followups:
        if registry[f.case_id]["severity"] == "severe":
            assert f.physio == "Dr. Deep Raj", f"Severe follow-up {f.fid} assigned to {f.physio}"
    print("  PASS: All severe cases and follow-ups assigned to Dr. Deep Raj")


# ----- Run all tests -----
test_registry_rejects_invalid_severity()
test_explain_severity_rule()
test_slotfinder_no_sundays_and_stops()
test_auto_reschedule_clears_missed()
test_max_per_day_not_exceeded()
test_v1_1_spec_requirements()
test_v1_2_spec_requirements()
test_severe_cases_assigned_to_dr_deep_raj()
print("\n  ALL TESTS PASSED")
