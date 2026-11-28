# Ngrok — Sports Injury Follow-up Scheduler

A full-stack sports injury follow-up scheduler with a **React + Three.js (`WebThreads`)** web UI, a **Flask** REST API, and an interactive Python console app. Schedules follow-up appointments, assigns rehab tasks, routes all `severe` cases to **Dr. Deep Raj**, and auto-reschedules missed follow-ups with rule explanations.

## How to run

> Run all commands below from the project root (`Sports-Injury-Follow-up-Scheduler`).

### First-time setup

```bash
python3 -m pip install flask flask-cors && (cd frontend && npm install)
```

### Run the Web App (starts both Backend + Frontend)

```bash
cd frontend && npm run dev
```

*(Vite automatically starts `api.py` on `http://127.0.0.1:5000` if it is not already running, or you can run `python3 api.py` in a separate terminal first.)*

Open **http://localhost:3000/** in your browser.

### Console App & Tests

```bash
python3 main.py          # Interactive menu
python3 main.py --demo   # Non-interactive demo
python3 test_smoke.py    # Smoke tests
```

## Menu options

| # | Action |
|---|--------|
| 1 | Add case |
| 2 | Schedule follow-up |
| 3 | Upcoming follow-ups |
| 4 | Missed follow-ups |
| 5 | Mark done |
| 6 | AUTO-RESCHEDULE missed |
| 7 | Today's queue |
| 8 | Set per-case interval override |
| 9 | Case history |
| 10 | Statistics |
| 11 | Audit log |
| 12 | Regenerate demo data |
| 0 | Exit |

## Topic mapping

| Topic | Where used |
|-------|-----------|
| int, float, str, bool, None | config.py (constants), store.py (age validation), rules.py (explain) |
| list | config.py (SPORTS, PHYSIOS), store.py (followups), scheduler.py |
| tuple | audit.py (AUDIT_LOG entries), store.py (FollowUp namedtuple) |
| dict | config.py (INJURY_TASKS, DEFAULT_RULES), store.py (CaseRegistry) |
| set | config.py (INJURY_TASKS values, SEVERITY_TASKS), scheduler.py (assign_tasks union) |
| functions (params, args, return) | All modules |
| local vs global scope | store.py (new_case_id, new_followup_id use `global`) |
| lambda | scheduler.py (get_upcoming, get_missed sort key) |
| list comprehension | scheduler.py (get_upcoming, get_missed, booked) |
| set comprehension | — (set union used instead) |
| dict comprehension | — (not needed) |
| iterators (__iter__, __next__, StopIteration) | scheduler.py (SlotFinder, PhysioRoundRobin) |
| decorators | audit.py (@audit), scheduler.py (@validate_case_id) |
| while / for / if | main.py (menu loop), store.py, scheduler.py |
| try / except | main.py (input validation, EOFError), store.py (CaseRegistry) |
| f-strings | All modules (output formatting) |
| UserDict subclass | store.py (CaseRegistry) |
| namedtuple | store.py (FollowUp) |
| OrderedDict | store.py (history per case) |
| Counter | scheduler.py (booked(), stats()) |
| defaultdict | scheduler.py (stats() missed by physio) |
| deque | scheduler.py (todays_queue) |
| ChainMap | rules.py (build_rules) |
