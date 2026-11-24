# main.py - Console UI for the Sports Injury Follow-up Scheduler
import sys       # Unit1: import
import os        # Unit1: import
import datetime  # Unit1: import

from config import (SPORTS, INJURY_TASKS, SEVERITIES, PHYSIOS,
                     CASE_OVERRIDES)
from audit import show_audit_log
from store import (registry, followups, history, generate_demo_data,
                   new_case_id, FollowUp)
from scheduler import (schedule_followup, get_upcoming, get_missed,
                       mark_done, auto_reschedule, todays_queue, stats)


# Unit1: f-string date format helper
def fmt(d):
    return d.strftime("%a %d-%b-%Y")


def clear_screen():
    # Unit1: if / bool / os.name
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def print_followup_table(fups, title):
    """Print a list of FollowUp records as a plain-text table."""
    print(f"\n  === {title} ({len(fups)} records) ===")
    if not fups:
        print("  (none)")
        return
    # Unit1: f-string with ljust
    print(f"  {'FID':<6} {'Case':<6} {'Name':<10} {'Sport':<12} "
          f"{'Injury':<22} {'Sev':<10} {'Due':<18} {'Physio':<12} {'Status':<10}")
    print(f"  {'-'*6} {'-'*6} {'-'*10} {'-'*12} "
          f"{'-'*22} {'-'*10} {'-'*18} {'-'*12} {'-'*10}")
    for f in fups:
        case = registry.get(f.case_id, {})
        name = case.get("name", "?")
        sport = case.get("sport", "?")
        injury = case.get("injury", "?")
        sev = case.get("severity", "?")
        print(f"  {f.fid:<6} {f.case_id:<6} {name:<10} {sport:<12} "
              f"{injury:<22} {sev:<10} {fmt(f.due):<18} {f.physio:<12} {f.status:<10}")


def menu_add_case():
    """Menu option 1: Add a new case."""
    print("\n  --- Add Case ---")
    name = input("  Name: ").strip()
    if not name:
        print("  Cancelled.")
        return

    try:
        age = int(input("  Age (10-60): ").strip())
    except (ValueError, EOFError):
        print("  Invalid age.")
        return

    print(f"  Sports: {', '.join(SPORTS)}")
    sport = input("  Sport: ").strip().lower()

    injuries = list(INJURY_TASKS.keys())
    print(f"  Injuries: {', '.join(injuries)}")
    injury = input("  Injury: ").strip().lower()

    print(f"  Severities: {', '.join(SEVERITIES)}")
    severity = input("  Severity: ").strip().lower()

    print(f"  Physios: {', '.join(PHYSIOS)}")
    physio = input("  Physio: ").strip()

    cid = new_case_id()
    try:
        registry[cid] = {
            "name": name, "age": age, "sport": sport,
            "injury": injury, "severity": severity, "physio": physio,
        }
        print(f"  Created case {cid} for {name}.")
    except ValueError as e:  # Unit1: try/except
        print(f"  Error: {e}")


def menu_schedule():
    """Menu option 2: Schedule a follow-up."""
    cid = input("  Case ID (e.g. C101): ").strip().upper()
    result = schedule_followup(cid)
    if result is not None:
        fu, explanation = result
        if fu is not None:
            print(f"  Scheduled {fu.fid} on {fmt(fu.due)} with {fu.physio}")
            print(f"  Why: {explanation}")
        else:
            print(f"  {explanation}")


def menu_mark_done():
    """Menu option 5: Mark a follow-up as done."""
    fid = input("  Follow-up ID (e.g. F001): ").strip().upper()
    result = mark_done(fid)
    print(f"  {result}")


def menu_auto_reschedule():
    """Menu option 6: Auto-reschedule missed follow-ups."""
    explanations = auto_reschedule()
    if not explanations:
        print("  No missed follow-ups to reschedule.")
        return
    print(f"\n  === AUTO-RESCHEDULE ({len(explanations)} rebooked) ===")
    for block in explanations:
        print(f"  {block}")
        print()


def menu_todays_queue():
    """Menu option 7: Today's queue with call-next."""
    q = todays_queue()
    if not q:
        print("  No follow-ups due today.")
        return
    print(f"  Today's queue: {len(q)} follow-ups")
    while q:
        f = q[0]
        case = registry.get(f.case_id, {})
        print(f"  Next: {f.fid} - {case.get('name','?')} ({case.get('injury','?')})")
        action = input("  Call next? (y/n): ").strip().lower()
        if action == "y":
            q.popleft()  # Unit1: deque.popleft
            mark_done(f.fid)
            print(f"  {f.fid} marked done.")
        else:
            break


def menu_set_override():
    """Menu option 8: Set a per-case interval override."""
    cid = input("  Case ID: ").strip().upper()
    if cid not in registry:
        print(f"  Case {cid} not found.")
        return
    try:
        days = int(input("  Custom interval_days: ").strip())
    except (ValueError, EOFError):
        print("  Invalid number.")
        return
    CASE_OVERRIDES[cid] = {"interval_days": days}
    print(f"  Override set for {cid}: interval_days={days}")


def menu_case_history():
    """Menu option 9: Show history for a case."""
    cid = input("  Case ID: ").strip().upper()
    if cid not in history:
        print(f"  No history for {cid}.")
        return
    print(f"\n  --- History for {cid} ---")
    for seq, event in history[cid].items():
        print(f"  [{seq}] {event}")


def menu_stats():
    """Menu option 10: Show statistics."""
    injury_counter, missed_by_physio, upcoming_c, missed_c, done_c = stats()
    print(f"\n  === Statistics ===")
    print(f"  Upcoming: {upcoming_c}  |  Missed: {missed_c}  |  Done: {done_c}")
    print(f"\n  Injury counts:")
    for injury, count in injury_counter.most_common():
        print(f"    {injury:<22} {count}")
    if missed_by_physio:
        print(f"\n  Missed by physio:")
        for physio, fids in missed_by_physio.items():
            print(f"    {physio:<12} {', '.join(fids)}")


# ----- Demo mode -----

def run_demo():
    """Non-interactive demo: summary, missed, reschedule, upcoming, audit."""
    generate_demo_data()

    print("=" * 70)
    print("  SPORTS INJURY FOLLOW-UP SCHEDULER  -  DEMO")
    print("=" * 70)

    # Summary
    print(f"\n  Demo data: {len(registry)} cases, {len(followups)} follow-ups")

    # Missed
    missed = get_missed()
    print_followup_table(missed, "MISSED FOLLOW-UPS")

    # Auto-reschedule
    explanations = auto_reschedule()
    if explanations:
        print(f"\n  === AUTO-RESCHEDULE ({len(explanations)} rebooked) ===")
        for block in explanations:
            print(f"  {block}")
            print()

    # Upcoming
    upcoming = get_upcoming()
    print_followup_table(upcoming, "UPCOMING FOLLOW-UPS")

    # Audit log
    print(f"\n  === AUDIT LOG ===")
    show_audit_log()

    print("\n  Demo complete.")


# ----- Interactive menu -----

def main():
    # Unit1: sys.argv
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
        return

    generate_demo_data()

    while True:  # Unit1: while loop
        try:
            clear_screen()
            print("\n  === SPORTS INJURY FOLLOW-UP SCHEDULER ===")
            print("  1  Add case")
            print("  2  Schedule follow-up")
            print("  3  Upcoming follow-ups")
            print("  4  Missed follow-ups")
            print("  5  Mark done")
            print("  6  AUTO-RESCHEDULE missed")
            print("  7  Today's queue")
            print("  8  Set per-case interval override")
            print("  9  Case history")
            print("  10 Statistics")
            print("  11 Audit log")
            print("  12 Regenerate demo data")
            print("  0  Exit")
            choice = input("\n  Choice: ").strip()

            if choice == "1":
                menu_add_case()
            elif choice == "2":
                menu_schedule()
            elif choice == "3":
                print_followup_table(get_upcoming(), "UPCOMING")
            elif choice == "4":
                print_followup_table(get_missed(), "MISSED")
            elif choice == "5":
                menu_mark_done()
            elif choice == "6":
                menu_auto_reschedule()
            elif choice == "7":
                menu_todays_queue()
            elif choice == "8":
                menu_set_override()
            elif choice == "9":
                menu_case_history()
            elif choice == "10":
                menu_stats()
            elif choice == "11":
                print(f"\n  === AUDIT LOG ===")
                show_audit_log()
            elif choice == "12":
                generate_demo_data()
                print("  Demo data regenerated.")
            elif choice == "0":
                print("  Goodbye!")
                sys.exit(0)  # Unit1: sys.exit
            else:
                print("  Invalid choice.")

            if choice != "0":
                input("\n  Press Enter to continue...")

        except (EOFError, KeyboardInterrupt):  # Unit1: try/except
            print("\n  Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
