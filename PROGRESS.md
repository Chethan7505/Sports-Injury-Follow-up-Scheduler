## 2026-11-24
Built entire project in one pass: config.py, audit.py, store.py, rules.py, scheduler.py, main.py, test_smoke.py, README.md.
All 5 smoke tests pass; `python main.py --demo` runs clean with 5 missed rescheduled.
Assumption: tasks in INJURY_TASKS/SEVERITY_TASKS chosen to match spec examples; demo seed 2026 produces deterministic data.
Next: interactive menu testing (Phase 1 demo ready).

## 2026-11-26
Added pick() helper for case-insensitive input matching; added 1-30 range check in menu_set_override.
Removed unused imports (datetime, FollowUp in main.py; OrderedDict, config in test_smoke.py).
Assumption: capped demo pending follow-ups at 3 per day in store.py so smoke tests stay valid on any date.
Next: Phase 1 viva demo.

## 2026-11-26 (v1.1)
Enforced data realism: max 3 per day, no same-case same-day duplicates, >=2 due today, >=5 missed (>=2 physios).
Implemented severity triage rescheduling (severe > moderate > mild, ties broken by oldest date).
Added slot note line for diverted appointments and updated default Why explanation text.
Individual rebooking events and count summary logged in audit; added v1.1 smoke tests.
Next: Phase 1 student viva presentation.

## 2026-11-26 (v1.2)
Only mark rebooked after slot found; initialize OrderedDict history on new cases; updated stats label.
Wrapped all generator expressions in comprehensions; added v1.2 rebooked count parity and scheduling smoke tests.
Next: Phase 1 project viva.
