# scheduler.py - Scheduling logic, iterators, and operations
import datetime  # Unit1: import
from collections import Counter, defaultdict, deque, OrderedDict  # Unit1: collections

from config import PHYSIOS, SEVERE_DOCTOR, INJURY_TASKS, SEVERITY_TASKS
from audit import audit, log_audit
from store import registry, followups, history, new_followup_id, FollowUp
from rules import build_rules, explain


# ----- Iterators -----

# Unit1: iterator class (__iter__, __next__, StopIteration)
class SlotFinder:
    """Yields dates from start, skipping Sundays, up to max_days ahead."""
    def __init__(self, start, max_days=14):
        self._current = start
        self._end = start + datetime.timedelta(days=max_days)

    def __iter__(self):  # Unit1: __iter__
        return self

    def __next__(self):  # Unit1: __next__
        while self._current <= self._end:
            day = self._current
            self._current = self._current + datetime.timedelta(days=1)
            if day.weekday() == 6:  # Unit1: if (skip Sunday)
                continue
            return day
        raise StopIteration  # Unit1: StopIteration


# Unit1: iterator class (infinite cycle)
class PhysioRoundRobin:
    """Cycles through PHYSIOS forever."""
    def __init__(self):
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        physio = PHYSIOS[self._index % len(PHYSIOS)]
        self._index = self._index + 1
        return physio


_physio_cycle = PhysioRoundRobin()  # module-level instance


# ----- Helper functions -----

def assign_tasks(case):
    """Return union of injury tasks and severity tasks."""
    # Unit1: set union
    return INJURY_TASKS[case["injury"]] | SEVERITY_TASKS[case["severity"]]


def booked():
    """Return Counter of due dates for pending follow-ups."""
    # Unit1: Counter / comprehension
    return Counter([f.due for f in followups if f.status == "pending"])


# ----- validate_case_id decorator -----

# Unit1: decorator with parameter validation
def validate_case_id(func):
    def wrapper(case_id, *args, **kwargs):
        if case_id not in registry:
            print(f"  Case {case_id} not found in registry.")
            return None
        return func(case_id, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# ----- Core scheduling (inner, undecorated) -----

def _schedule_followup_inner(case_id, start=None):
    """Schedule a new follow-up for a case. Returns (FollowUp, explanation) or (None, msg)."""
    today = datetime.date.today()
    rules = build_rules(case_id)
    interval = rules["interval_days"]
    max_per_day = rules["max_per_day"]

    earliest = (start or today) + datetime.timedelta(days=interval)
    slots = SlotFinder(earliest)
    current_booked = booked()
    case_pending_dates = {f.due for f in followups if f.case_id == case_id and f.status == "pending"}

    for day in slots:  # Unit1: for with iterator
        if current_booked[day] < max_per_day and day not in case_pending_dates:
            case = registry[case_id]
            physio = SEVERE_DOCTOR if case["severity"] == "severe" else next(_physio_cycle)
            tasks = assign_tasks(case)
            fid = new_followup_id()
            fu = FollowUp(fid=fid, case_id=case_id, due=day,
                          physio=physio, status="pending", tasks=tasks)
            followups.append(fu)

            # Build explanation
            layer, value, overridden = explain(rules, "interval_days")
            if layer == "default":
                explanation = f"interval_days = {value} from the DEFAULT rule (no sport/severity rule matched)"
            else:
                explanation = f"interval_days = {value} from the {layer.upper()}"
                if overridden:
                    parts = [f"{ln} = {v}" for ln, v in overridden]  # Unit1: list comprehension
                    explanation = explanation + f"\n           (overrode: {', '.join(parts)})"

            # Log to history
            if case_id not in history:
                history[case_id] = OrderedDict()
            seq = len(history[case_id])
            history[case_id][seq] = f"{fid} scheduled on {day.strftime('%a %d-%b-%Y')}"

            return (fu, explanation)

    return (None, f"No slot found for {case_id} within 14 days")


# Public decorated version
@audit
@validate_case_id
def schedule_followup(case_id, start=None):
    """Schedule a follow-up (audited + validated)."""
    return _schedule_followup_inner(case_id, start)


# ----- Queries -----

def get_upcoming():
    """Pending follow-ups due today or later, sorted by due date."""
    today = datetime.date.today()
    # Unit1: list comprehension with lambda sort
    return sorted(
        [f for f in followups if f.status == "pending" and f.due >= today],
        key=lambda f: f.due,
    )


def get_missed():
    """Pending follow-ups with due date before today, sorted by due date."""
    today = datetime.date.today()
    # Unit1: list comprehension with lambda sort
    return sorted(
        [f for f in followups if f.status == "pending" and f.due < today],
        key=lambda f: f.due,
    )


@audit
def mark_done(fid):
    """Mark a follow-up as done by fid."""
    for i, f in enumerate(followups):  # Unit1: for / enumerate
        if f.fid == fid:
            followups[i] = f._replace(status="done")  # Unit1: namedtuple._replace
            return f"Marked {fid} as done"
    return f"{fid} not found"


@audit
def auto_reschedule():
    """Reschedule all missed follow-ups. Return list of explanation blocks."""
    # Unit1: sorted with lambda key / dict lookup / tuple comparison (triage order)
    severity_rank = {"severe": 0, "moderate": 1, "mild": 2}
    missed = sorted(
        get_missed(),
        key=lambda f: (severity_rank.get(registry[f.case_id]["severity"], 99), f.due)
    )
    explanations = []  # Unit1: list
    today = datetime.date.today()

    for f in missed:
        case = registry[f.case_id]
        rules = build_rules(f.case_id)
        interval = rules["interval_days"]
        wanted_date = today + datetime.timedelta(days=interval)

        result = _schedule_followup_inner(f.case_id, start=today)
        if result is None:
            continue
        new_fu, why = result

        if new_fu is None:
            explanations.append(f"{f.fid} | {case['name']} | NOT rebooked: {why}")
            continue

        # Mark old as rebooked only after successful booking
        for i, fu in enumerate(followups):
            if fu.fid == f.fid:
                followups[i] = fu._replace(status="rebooked")
                break

        tasks_str = ", ".join(sorted(new_fu.tasks))
        slot_note = (
            f"  -> Slot note: wanted {wanted_date.strftime('%a %d-%b-%Y')} (full or unavailable), next free slot used\n"
            if new_fu.due != wanted_date else ""
        )
        block = (
            f"{f.fid} | {case['name']} ({case['sport']}, {case['injury']}, "
            f"{case['severity'].upper()}) | missed {f.due.strftime('%a %d-%b-%Y')}\n"
            f"  -> Rescheduled: {new_fu.due.strftime('%a %d-%b-%Y')} with {new_fu.physio}\n"
            f"  -> Tasks: {tasks_str}\n"
            f"{slot_note}"
            f"  -> Why: {why}"
        )
        explanations.append(block)
        log_audit("auto_reschedule",
                  f"{f.fid} -> {new_fu.fid} ({new_fu.case_id}, {new_fu.due.strftime('%a %d-%b-%Y')})")

    return explanations


def todays_queue():
    """Return a deque of pending follow-ups due today."""
    today = datetime.date.today()
    # Unit1: deque / comprehension
    return deque([f for f in followups if f.status == "pending" and f.due == today])


def stats():
    """Return injury Counter, missed-by-physio defaultdict, and status counts."""
    # Unit1: Counter
    injury_counter = Counter([registry[f.case_id]["injury"]
                             for f in followups if f.case_id in registry])
    # Unit1: defaultdict
    missed_by_physio = defaultdict(list)
    for f in get_missed():
        missed_by_physio[f.physio].append(f.fid)

    upcoming_count = len(get_upcoming())
    missed_count = len(get_missed())
    done_count = len([f for f in followups if f.status == "done"])

    return injury_counter, missed_by_physio, upcoming_count, missed_count, done_count
