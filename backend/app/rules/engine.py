"""
Rule evaluation engine.
"""
import json
import re
from typing import List, Optional


OPERATORS = {
    "equals": lambda a, b: str(a) == str(b),
    "not_equals": lambda a, b: str(a) != str(b),
    "contains": lambda a, b: str(b) in str(a),
    "not_contains": lambda a, b: str(b) not in str(a),
    "in": lambda a, b: str(a) in b if isinstance(b, list) else str(a) in [str(b)],
    "not_in": lambda a, b: str(a) not in b if isinstance(b, list) else str(a) not in [str(b)],
    "greater_than": lambda a, b: float(a) > float(b),
    "less_than": lambda a, b: float(a) < float(b),
    "regex_match": lambda a, b: bool(re.search(b, str(a))),
}


def evaluate_condition(alert: dict, condition: dict) -> bool:
    field = condition.get("field", "")
    operator = condition.get("operator", "")
    value = condition.get("value")

    alert_value = alert.get(field)
    if alert_value is None:
        return False

    op_func = OPERATORS.get(operator)
    if not op_func:
        return False

    try:
        return op_func(alert_value, value)
    except (ValueError, TypeError):
        return False


def evaluate_rule(alert: dict, conditions: dict) -> bool:
    logic = conditions.get("logic", "AND").upper()
    condition_list = conditions.get("conditions", [])

    if not condition_list:
        return False

    results = [evaluate_condition(alert, c) for c in condition_list]

    if logic == "OR":
        return any(results)
    return all(results)


def apply_actions(alert: dict, actions: list) -> dict:
    modified = dict(alert)
    for action in actions:
        action_type = action.get("type")
        if action_type == "set_severity":
            modified["severity"] = action.get("value", alert.get("severity"))
        elif action_type == "add_tag":
            tag = action.get("value", "")
            if tag and tag not in modified.get("attack_type", ""):
                modified["attack_type"] = f"{modified.get('attack_type', '')},{tag}"
        elif action_type == "set_attack_type":
            modified["attack_type"] = action.get("value", alert.get("attack_type"))
    return modified


def process_alert_with_rules(alert: dict, rules: list) -> dict:
    modified = alert
    for rule in rules:
        if not rule.get("is_enabled", True):
            continue

        conditions = json.loads(rule["conditions"]) if isinstance(rule["conditions"], str) else rule["conditions"]
        actions = json.loads(rule["actions"]) if isinstance(rule["actions"], str) else rule["actions"]

        if evaluate_rule(modified, conditions):
            modified = apply_actions(modified, actions)
            rule["match_count"] = rule.get("match_count", 0) + 1

    return modified
