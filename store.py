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
            due = _shift_off_sunday(today + datetime.timedelta(days=offset))
            fid = new_followup_id()
            tasks = INJURY_TASKS[injury] | SEVERITY_TASKS[severity]  # Unit1: set union

            if due < today:
                status = random.choice(["done", "pending"])
            else:
                status = "pending"

            # Unit1: while loop (cap pending bookings per day at 3)
            while status == "pending" and sum(1 for f in followups if f.status == "pending" and f.due == due) >= 3:
                due = _shift_off_sunday(due + datetime.timedelta(days=1))

            fu = FollowUp(fid=fid, case_id=cid, due=due,
                          physio=physio, status=status, tasks=tasks)
            followups.append(fu)
            seq = len(history[cid])
            history[cid][seq] = f"{fid} scheduled on {due.strftime('%a %d-%b-%Y')}"

    # --- GUARANTEE minimums ---
    # Ensure at least 3 missed (past + pending)
    past_pending = [i for i, f in enumerate(followups)
                    if f.due < today and f.status == "pending"]
    need_missed = 3 - len(past_pending)
    if need_missed > 0:
        # Find past done records and flip to pending
        past_done = [i for i, f in enumerate(followups)
                     if f.due < today and f.status == "done"]
        for idx in past_done[:need_missed]:
            followups[idx] = followups[idx]._replace(status="pending")
            need_missed = need_missed - 1
        # If still short, move some future follow-ups to the past
        while need_missed > 0:
            future = [i for i, f in enumerate(followups)
                      if f.due >= today and f.status == "pending"]
            if not future:
                break
            idx = future[0]
            new_due = _shift_off_sunday(today - datetime.timedelta(days=random.randint(1, 5)))
            followups[idx] = followups[idx]._replace(due=new_due, status="pending")
            need_missed = need_missed - 1

    # Ensure at least 5 upcoming (today or later + pending)
    upcoming = [i for i, f in enumerate(followups)
                if f.due >= today and f.status == "pending"]
    need_upcoming = 5 - len(upcoming)
    while need_upcoming > 0:
        # pick a random case and add a future follow-up
        cid = random.choice(list(registry.keys()))
        case = registry[cid]
        offset = random.randint(1, 10)
        due = _shift_off_sunday(today + datetime.timedelta(days=offset))
        fid = new_followup_id()
        tasks = INJURY_TASKS[case["injury"]] | SEVERITY_TASKS[case["severity"]]
        fu = FollowUp(fid=fid, case_id=cid, due=due,
                      physio=case["physio"], status="pending", tasks=tasks)
        followups.append(fu)
        seq = len(history[cid])
        history[cid][seq] = f"{fid} scheduled on {due.strftime('%a %d-%b-%Y')}"
        need_upcoming = need_upcoming - 1

    # Ensure at least 2 done
    done_count = len([f for f in followups if f.status == "done"])
    need_done = 2 - done_count
    if need_done > 0:
        past_pending2 = [i for i, f in enumerate(followups)
                         if f.due < today and f.status == "pending"]
        # Only flip extras beyond the 3 we guaranteed as missed
        available = past_pending2[3:]
        for idx in available[:need_done]:
            followups[idx] = followups[idx]._replace(status="done")
            need_done = need_done - 1
        # If still need done, create new past done records
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
