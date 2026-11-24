# config.py - Constants for the Sports Injury Follow-up Scheduler

# Unit1: list (mutable sequence of sports)
SPORTS = ["cricket", "football", "kabaddi", "athletics", "badminton", "hockey"]

# Unit1: dict -> set (injury to task mapping)
INJURY_TASKS = {
    "ankle sprain":          {"ice therapy", "mobility test", "brace fitting"},
    "hamstring strain":      {"ice therapy", "strength drill", "mobility test"},
    "ACL tear":              {"X-ray review", "strength drill", "mobility test"},
    "fracture":              {"X-ray review", "brace fitting", "ice therapy"},
    "concussion":            {"cognitive check", "mobility test"},
    "shoulder dislocation":  {"X-ray review", "strength drill", "brace fitting"},
    "tennis elbow":          {"ice therapy", "strength drill", "brace fitting"},
}

# Unit1: list of str (severity levels)
SEVERITIES = ["mild", "moderate", "severe"]

# Unit1: dict -> set (severity to extra tasks)
SEVERITY_TASKS = {
    "mild":     {"ice therapy"},
    "moderate": {"mobility test", "strength drill"},
    "severe":   {"specialist review", "strength drill", "X-ray review"},
}

# Unit1: list of str
PHYSIOS = ["Dr. Meera", "Dr. Arjun", "Dr. Kavya"]

# Unit1: dict (default scheduling rules)
DEFAULT_RULES = {"interval_days": 7, "max_per_day": 3}

# Unit1: dict of dict (sport-specific overrides)
SPORT_RULES = {
    "football":  {"interval_days": 5},
    "kabaddi":   {"interval_days": 5},
    "athletics": {"interval_days": 6},
}

# Unit1: dict of dict (severity-specific overrides)
SEVERITY_RULES = {
    "moderate": {"interval_days": 4},
    "severe":   {"interval_days": 2},
}

# Unit1: dict (mutable, filled at runtime)
CASE_OVERRIDES = {}

# Unit1: list of str (layer names aligned with ChainMap index)
LAYER_NAMES = ["case override", "severity rule", "sport rule", "default"]

# Unit1: list of str (fictional first names for demo data)
FIRST_NAMES = [
    "Ravi", "Priya", "Arjun", "Sneha", "Kiran",
    "Meena", "Vikram", "Anita", "Suresh", "Deepa",
    "Rahul", "Kavita",
]
