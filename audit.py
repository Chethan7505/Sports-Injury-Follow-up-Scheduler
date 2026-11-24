# audit.py - Audit logging decorator and log viewer
import datetime  # Unit1: import

# Unit1: list of tuples (audit log storage)
AUDIT_LOG = []


# Unit1: decorator (wraps a function to log its calls)
def audit(func):
    def wrapper(*args, **kwargs):  # Unit1: *args, **kwargs
        result = func(*args, **kwargs)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        summary = str(result)[:60] if result is not None else "ok"
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
