# rules.py - Layered rule resolution with ChainMap
from collections import ChainMap  # Unit1: collections.ChainMap

from config import (DEFAULT_RULES, SPORT_RULES, SEVERITY_RULES,
                     CASE_OVERRIDES, LAYER_NAMES)
from store import registry


def build_rules(case_id):
    """Build a 4-layer ChainMap for a case (index aligns with LAYER_NAMES)."""
    case = registry[case_id]
    sev = case["severity"]
    sport = case["sport"]
    # Unit1: ChainMap (first map wins on lookup)
    return ChainMap(
        CASE_OVERRIDES.get(case_id, {}),   # layer 0: case override
        SEVERITY_RULES.get(sev, {}),       # layer 1: severity rule
        SPORT_RULES.get(sport, {}),        # layer 2: sport rule
        DEFAULT_RULES,                     # layer 3: default
    )


def explain(rules, key):
    """Return (winning_layer, value, [(overridden_layer, value), ...])."""
    winning_layer = None  # Unit1: None
    winning_value = None
    overridden = []  # Unit1: list
    found = False  # Unit1: bool

    for i, m in enumerate(rules.maps):  # Unit1: for / enumerate
        if key in m:
            if not found:
                winning_layer = LAYER_NAMES[i]
                winning_value = m[key]
                found = True
            else:
                overridden.append((LAYER_NAMES[i], m[key]))

    return (winning_layer, winning_value, overridden)  # Unit1: tuple return
