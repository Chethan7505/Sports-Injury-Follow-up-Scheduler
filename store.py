# store.py - Data storage: CaseRegistry, FollowUp, demo data
import random          # Unit1: import
import datetime        # Unit1: import
from collections import namedtuple, UserDict, OrderedDict  # Unit1: collections

from config import (SPORTS, INJURY_TASKS, SEVERITIES, SEVERITY_TASKS,
                     PHYSIOS, FIRST_NAMES)

# Unit1: namedtuple (immutable record)
FollowUp = namedtuple("FollowUp", "fid case_id due physio status tasks")


# Unit1: UserDict subclass (validates on insert)
class CaseRegistry(UserDict):
    def __setitem__(self, key, case):
        # Unit1: if / bool / str checks
        if not isinstance(case, dict):
            raise ValueError("Case must be a dict")
        for field in ("name", "age", "sport", "injury", "severity", "physio"):
            if field not in case:
                raise ValueError(f"Missing field: {field}")
        age = case["age"]
        if not isinstance(age, int) or age < 10 or age > 60:
            raise ValueError(f"Age must be int 10-60, got {age}")
        if case["sport"] not in SPORTS:
            raise ValueError(f"Unknown sport: {case['sport']}")
        if case["severity"] not in SEVERITIES:
            raise ValueError(f"Unknown severity: {case['severity']}")
        if case["injury"] not in INJURY_TASKS:
            raise ValueError(f"Unknown injury: {case['injury']}")
        if case["physio"] not in PHYSIOS:
            raise ValueError(f"Unknown physio: {case['physio']}")
        super().__setitem__(key, case)


# --- Module-level (global) state ---
registry = CaseRegistry()          # Unit1: global scope
followups = []                     # Unit1: list
history = {}                       # Unit1: dict (case_id -> OrderedDict)
next_case_no = 101                 # Unit1: int
next_fid = 1                       # Unit1: int


def new_case_id():
    """Return e.g. 'C101' and bump the counter."""
    global next_case_no  # Unit1: global scope
    cid = f"C{next_case_no}"
    next_case_no = next_case_no + 1
    return cid


def new_followup_id():
    """Return e.g. 'F001' and bump the counter."""
    global next_fid  # Unit1: global scope
    fid = f"F{next_fid:03d}"
    next_fid = next_fid + 1
    return fid


def _shift_off_sunday(d):
    """If d is Sunday (weekday==6), shift to Monday."""
    if d.weekday() == 6:  # Unit1: if
        return d + datetime.timedelta(days=1)
    return d


def _find_demo_slot(cid, start_date, direction=1):
    """Find a date (skipping Sundays) with < 3 pending and no pending for cid."""
    d = start_date
    if d.weekday() == 6:
        d = d + datetime.timedelta(days=1 if direction >= 0 else -1)
    while True:
        if d.weekday() != 6:
            pending_count = sum([1 for f in followups if f.status == "pending" and f.due == d])
            case_has_pending = any([f.case_id == cid and f.due == d and f.status == "pending" for f in followups])
            if pending_count < 3 and not case_has_pending:
                return d
        d = d + datetime.timedelta(days=1 if direction >= 0 else -1)


def generate_demo_data(seed=2026):
    """Create 12 fictional cases with follow-ups for demonstration."""
    global next_case_no, next_fid  # Unit1: global scope
    random.seed(seed)  # Unit1: function call

    # Clear all state
    registry.data.clear()
    followups.clear()
    history.clear()
    next_case_no = 101
    next_fid = 1

    today = datetime.date.today()
    injuries = list(INJURY_TASKS.keys())  # Unit1: list()

    # Create 12 cases
    for i in range(12):  # Unit1: for loop
        cid = new_case_id()
        name = FIRST_NAMES[i]
        age = random.randint(16, 45)
        sport = random.choice(SPORTS)
        injury = random.choice(injuries)
        severity = random.choice(SEVERITIES)
        physio = random.choice(PHYSIOS)
        case = {
            "name": name, "age": age, "sport": sport,
            "injury": injury, "severity": severity, "physio": physio,
        }
        registry[cid] = case
        history[cid] = OrderedDict()  # Unit1: OrderedDict
        history[cid][0] = f"Case created for {name}"

        # 1-2 follow-ups per case
        num_fups = random.randint(1, 2)
        for _ in range(num_fups):
            offset = random.randint(-9, 10)
            initial_due = _shift_off_sunday(today + datetime.timedelta(days=offset))
            fid = new_followup_id()
            tasks = INJURY_TASKS[injury] | SEVERITY_TASKS[severity]  # Unit1: set union

            if initial_due < today:
                status = random.choice(["done", "pending"])
            else:
                status = "pending"

            if status == "pending":
                direction = -1 if initial_due < today else 1
                due = _find_demo_slot(cid, initial_due, direction=direction)
                if initial_due < today and due >= today:
                    due = _find_demo_slot(cid, today - datetime.timedelta(days=1), direction=-1)
            else:
                due = initial_due

            fu = FollowUp(fid=fid, case_id=cid, due=due,
                          physio=physio, status=status, tasks=tasks)
            followups.append(fu)

    # --- GUARANTEE requirements ---
    # 1. At least 5 missed (due < today and pending)
    past_pending = [i for i, f in enumerate(followups)
                    if f.due < today and f.status == "pending"]
    need_missed = 5 - len(past_pending)
    if need_missed > 0:
        for idx, f in enumerate(followups):
            if need_missed <= 0:
                break
            if f.due < today and f.status == "done":
                slot = _find_demo_slot(f.case_id, f.due, direction=-1)
                if slot < today:
                    followups[idx] = f._replace(due=slot, status="pending")
                    need_missed = need_missed - 1

    while need_missed > 0:
        future = [i for i, f in enumerate(followups)
                  if f.due > today and f.status == "pending"]
        if not future:
            break
        idx = future[0]
        f = followups[idx]
        slot = _find_demo_slot(f.case_id, today - datetime.timedelta(days=1), direction=-1)
        followups[idx] = f._replace(due=slot, status="pending")
        need_missed = need_missed - 1

    # Ensure at least 2 different physios among missed
    missed_fups = [f for f in followups if f.due < today and f.status == "pending"]
    physios_in_missed = {f.physio for f in missed_fups}
    if len(physios_in_missed) < 2 and missed_fups:
        current_p = missed_fups[0].physio
        alt_p = [p for p in PHYSIOS if p != current_p][0]
        for idx, f in enumerate(followups):
            if f.fid == missed_fups[0].fid:
                followups[idx] = f._replace(physio=alt_p)
                break

    # 2. At least 2 pending follow-ups of DIFFERENT cases due TODAY
    today_pending = [f for f in followups if f.due == today and f.status == "pending"]
    today_cases = {f.case_id for f in today_pending}
    if len(today_cases) < 2:
        for cid in registry:
            if len(today_cases) >= 2:
                break
            if cid in today_cases:
                continue
            current_today_count = sum([1 for f in followups if f.due == today and f.status == "pending"])
            if current_today_count >= 3:
                break
            candidate_idxs = [i for i, f in enumerate(followups)
                              if f.case_id == cid and f.status == "pending" and f.due > today]
            if candidate_idxs:
                idx = candidate_idxs[0]
                followups[idx] = followups[idx]._replace(due=today)
            else:
                case = registry[cid]
                fid = new_followup_id()
                tasks = INJURY_TASKS[case["injury"]] | SEVERITY_TASKS[case["severity"]]
                fu = FollowUp(fid=fid, case_id=cid, due=today,
                              physio=case["physio"], status="pending", tasks=tasks)
                followups.append(fu)
            today_cases.add(cid)

    # 3. Ensure at least 5 upcoming (today or later + pending)
    while len([f for f in followups if f.due >= today and f.status == "pending"]) < 5:
        cid = random.choice(list(registry.keys()))
        case = registry[cid]
        slot = _find_demo_slot(cid, today + datetime.timedelta(days=random.randint(1, 10)), direction=1)
        fid = new_followup_id()
        tasks = INJURY_TASKS[case["injury"]] | SEVERITY_TASKS[case["severity"]]
        fu = FollowUp(fid=fid, case_id=cid, due=slot,
                      physio=case["physio"], status="pending", tasks=tasks)
        followups.append(fu)

    # 4. Ensure at least 2 done
    done_count = len([f for f in followups if f.status == "done"])
    need_done = 2 - done_count
    if need_done > 0:
        past_pending_idxs = [i for i, f in enumerate(followups)
                             if f.due < today and f.status == "pending"]
        available = past_pending_idxs[5:]  # preserve at least 5 missed
        for idx in available[:need_done]:
            followups[idx] = followups[idx]._replace(status="done")
            need_done = need_done - 1
        while need_done > 0:
            cid = random.choice(list(registry.keys()))
            case = registry[cid]
            due = _shift_off_sunday(today - datetime.timedelta(days=random.randint(1, 9)))
            fid = new_followup_id()
            tasks = INJURY_TASKS[case["injury"]] | SEVERITY_TASKS[case["severity"]]
            fu = FollowUp(fid=fid, case_id=cid, due=due,
                          physio=case["physio"], status="done", tasks=tasks)
            followups.append(fu)
            need_done = need_done - 1

    # Rebuild history
    history.clear()
    for cid, case in registry.items():
        history[cid] = OrderedDict()
        history[cid][0] = f"Case created for {case['name']}"
    for f in followups:
        if f.case_id in history:
            seq = len(history[f.case_id])
            history[f.case_id][seq] = f"{f.fid} scheduled on {f.due.strftime('%a %d-%b-%Y')}"
