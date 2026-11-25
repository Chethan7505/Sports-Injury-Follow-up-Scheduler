# Sports Injury Follow-up Scheduler - Spec v1

## 1. Purpose
Console app. A sports department uses FICTIONAL injury cases to schedule follow-up appointments
and assign rehab tasks. It lists upcoming and missed follow-ups.
HEADLINE FEATURE ("self-healing schedule"): missed follow-ups are rescheduled automatically and the
program EXPLAINS which rule chose the new date.

## 2. Files (create exactly these)
config.py, audit.py, store.py, rules.py, scheduler.py, main.py, test_smoke.py, README.md.
Dependency order, no circular imports: config -> audit -> store -> rules -> scheduler -> main.
README.md: how to run, menu list, and a table mapping each Unit 1 topic to where it is used.

## 3. config.py (constants only)
- SPORTS: cricket, football, kabaddi, athletics, badminton, hockey.
- INJURY_TASKS: dict injury -> set of tasks. Injuries: ankle sprain, hamstring strain, ACL tear,
  fracture, concussion, shoulder dislocation, tennis elbow. Tasks e.g. "ice therapy",
  "mobility test", "X-ray review", "strength drill", "cognitive check", "brace fitting".
- SEVERITIES: mild, moderate, severe. SEVERITY_TASKS: dict severity -> set (severe adds "specialist review").
- PHYSIOS: ["Dr. Meera", "Dr. Arjun", "Dr. Kavya"].
- DEFAULT_RULES = {"interval_days": 7, "max_per_day": 3}
- SPORT_RULES = {"football": {"interval_days": 5}, "kabaddi": {"interval_days": 5},
  "athletics": {"interval_days": 6}} (other sports have no entry)
- SEVERITY_RULES = {"moderate": {"interval_days": 4}, "severe": {"interval_days": 2}} (mild has no entry)
- CASE_OVERRIDES = {} (mutable, filled at runtime)
- LAYER_NAMES = ["case override", "severity rule", "sport rule", "default"]
- Fictional first-name list for demo data.

## 4. audit.py
- AUDIT_LOG list of tuples.
- Decorator audit(func): wrapper(*args, **kwargs) calls func, appends (HH:MM:SS via
  datetime.now().strftime, func.__name__, short result summary), returns result.
  Set wrapper.__name__ = func.__name__ manually (no functools).
- show_audit_log() prints the log.

## 5. store.py
- FollowUp = namedtuple("FollowUp", "fid case_id due physio status tasks")
  status in: "pending", "done", "rebooked". Never mutate; use ._replace().
- class CaseRegistry(UserDict): __setitem__ validates the case dict
  {name, age, sport, injury, severity, physio}: age int 10-60, sport/severity/injury/physio must be
  known values; raise ValueError with a clear message.
- Module-level (global) state: registry, followups (list), history (dict case_id -> OrderedDict
  seq_number -> event text), counters next_case_no / next_fid.
  new_case_id() and new_followup_id() use the `global` keyword  # Unit1: global scope.
- generate_demo_data(seed=2026): random.seed(seed); clear state; create 12 fictional cases
  (ids C101..C112) with random but valid fields; 1-2 follow-ups each, due = today + random offset
  -9..+10 days (shift off Sundays). Past due: random status done/pending. After generating,
  GUARANTEE at least 3 missed (past + pending), 5 upcoming, 2 done by adjusting records.
  Log creation events into history.

## 6. rules.py
- build_rules(case_id) -> ChainMap(CASE_OVERRIDES.get(case_id, {}), SEVERITY_RULES.get(sev, {}),
  SPORT_RULES.get(sport, {}), DEFAULT_RULES). Always 4 maps so index aligns with LAYER_NAMES.
- explain(rules, key) -> (winning_layer_name, value, list of (overridden_layer_name, value)),
  found by looping over rules.maps.

## 7. scheduler.py
- class SlotFinder: iterator. __init__(start, max_days=14). __next__ skips Sundays
  (weekday()==6), returns the next date, raises StopIteration after start+max_days.
- class PhysioRoundRobin: iterator that cycles through PHYSIOS forever.
- assign_tasks(case) -> INJURY_TASKS[injury] | SEVERITY_TASKS[severity]  (set union).
- booked() -> Counter of due dates of pending follow-ups (computed fresh each call).
- schedule_followup(case_id, start=None) [decorated with @audit]: interval from build_rules;
  earliest = (start or today) + interval; iterate SlotFinder(earliest), take first day where
  booked()[day] < max_per_day; physio from PhysioRoundRobin; create FollowUp; append; add history
  event; return (followup, explanation text). If no slot, return (None, message).
- get_upcoming(): comprehension, pending and due >= today, sorted with lambda by due.
- get_missed(): comprehension, pending and due < today, sorted by due.
- mark_done(fid) [@audit]: replace record with status "done".
- auto_reschedule() [@audit]: for each missed follow-up: mark old as "rebooked", call
  schedule_followup(case_id, start=today). Return list of explanation blocks (see sample).
- todays_queue(): deque of pending follow-ups due today; menu allows popleft() "call next" -> done.
- stats(): Counter of injuries; defaultdict(list) of missed follow-ups by physio; counts of
  upcoming/missed/done.
- validate_case_id decorator: if case id not in registry, print a friendly message and return None.

## 8. main.py
- Date format everywhere: d.strftime("%a %d-%b-%Y").
- Clear screen only if sys.stdout.isatty(): os.system("cls" if os.name == "nt" else "clear").
- Menu loop (while True):
  1 Add case  2 Schedule follow-up  3 Upcoming  4 Missed  5 Mark done
  6 AUTO-RESCHEDULE missed  7 Today's queue  8 Set per-case interval override
  9 Case history  10 Statistics  11 Audit log  12 Regenerate demo data  0 Exit (sys.exit)
- All input validated; never crash on bad input; handle EOFError/KeyboardInterrupt with a clean exit.
- `python main.py --demo` (use sys.argv): non-interactive. Prints demo data summary, MISSED list,
  runs AUTO-RESCHEDULE with explanations, then UPCOMING list, then audit log, then exits.
- Tables are plain text built with f-strings and ljust (no libraries).

## 9. Sample explanation block (match this style)
F004 | Ravi (kabaddi, ACL tear, SEVERE) | missed Fri 20-Nov-2026
  -> Rescheduled: Thu 26-Nov-2026 with Dr. Meera
  -> Tasks: X-ray review, strength drill, specialist review
  -> Why: interval_days = 2 from the SEVERITY rule
          (overrode: sport rule = 5, default = 7)

## 10. test_smoke.py (plain asserts, no test framework, prints "ALL TESTS PASSED")
- Registry rejects an invalid severity.
- explain() reports "severity rule" for a severe kabaddi case.
- SlotFinder yields no Sundays and stops (StopIteration) at the limit.
- After generate_demo_data and auto_reschedule: get_missed() is empty.
- No day exceeds max_per_day pending follow-ups.

## 11. Done when
python test_smoke.py passes AND python main.py --demo runs without errors AND no forbidden import exists.

## 12. v1.1 changes
- P1: Capped dates to max 3 pending; prevented same-case same-day duplicates in demo & scheduler.
- P1: Guaranteed >=5 missed (>=2 physios) and >=2 pending of different cases due today.
- P2: auto_reschedule sorts missed follow-ups by severity triage, then oldest due date.
- P2: Added slot note for unavailable wanted dates; updated default Why message.
- P3: Audit logs individual rebookings (old -> new) and count summary, no raw lists.
- P4: Smoke tests expanded for v1.1 data realism, today's queue, and triage assertions.