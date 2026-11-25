# audit.py - Audit logging decorator and log viewer
import datetime  # Unit1: import

# Unit1: list of tuples (audit log storage)
AUDIT_LOG = []


def log_audit(func_name, summary):
    """Add a single entry to AUDIT_LOG with current timestamp."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    AUDIT_LOG.append((timestamp, func_name, str(summary)[:60]))  # Unit1: tuple


# Unit1: decorator (wraps a function to log its calls)
def audit(func):
    def wrapper(*args, **kwargs):  # Unit1: *args, **kwargs
        result = func(*args, **kwargs)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        if func.__name__ == "auto_reschedule":
            count = len(result) if isinstance(result, list) else 0
            summary = f"{count} follow-ups rebooked"
        elif isinstance(result, list):
            summary = f"{len(result)} items"
        elif result is not None:
            summary = str(result)[:60]
        else:
            summary = "ok"
        AUDIT_LOG.append((timestamp, func.__name__, summary))  # Unit1: tuple
        return result
    wrapper.__name__ = func.__name__  # Unit1: manual name copy (no functools)
    return wrapper


def show_audit_log():
    """Print the entire audit log."""
    if not AUDIT_LOG:
        print("  (audit log is empty)")
        return
    print(f"  {'Time':<10} {'Function':<22} {'Summary'}")
    print(f"  {'-'*10} {'-'*22} {'-'*40}")
    for timestamp, name, summary in AUDIT_LOG:  # Unit1: tuple unpacking
        print(f"  {timestamp:<10} {name:<22} {summary}")
