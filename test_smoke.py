# test_smoke.py - Smoke tests (plain asserts, no test framework)
import datetime

from store import CaseRegistry, generate_demo_data, followups, registry
from rules import build_rules, explain
from scheduler import SlotFinder, get_missed, auto_reschedule, booked


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
        "injury": "ACL tear", "severity": "severe", "physio": "Dr. Meera",
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


# ----- Run all tests -----
test_registry_rejects_invalid_severity()
test_explain_severity_rule()
test_slotfinder_no_sundays_and_stops()
test_auto_reschedule_clears_missed()
test_max_per_day_not_exceeded()
print("\n  ALL TESTS PASSED")
