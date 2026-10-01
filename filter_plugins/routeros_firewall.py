"""Controller-side RouterOS firewall parsing and compliance filters."""

from __future__ import annotations

import re
from typing import Any


KEY_RE = re.compile(r"(?:^|\s)([A-Za-z0-9_.-]+)=")


def _unquote(value: str) -> str:
    value = value.strip()

    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]

    return value.replace(r'\"', '"').replace(r'\\', '\\')


def _parse_line(line: str) -> dict[str, Any]:
    line = line.strip()

    matches = list(KEY_RE.finditer(line))

    if not matches:
        return {}

    prefix = line[:matches[0].start()].strip()
    flags = set(prefix.split())

    rule: dict[str, Any] = {
        "_raw": line,
        "_index": next(
            (x for x in flags if x.isdigit()),
            None,
        ),
        "_disabled": "X" in flags,
        "_dynamic": "D" in flags,
        "_invalid": "I" in flags,
    }

    for i, match in enumerate(matches):
        key = match.group(1)

        start = match.end()
        end = (
            matches[i + 1].start()
            if i + 1 < len(matches)
            else len(line)
        )

        rule[key] = _unquote(line[start:end])

    return rule


def parse_routeros_rules(lines: Any) -> list[dict[str, Any]]:
    if lines is None:
        return []

    return [
        rule
        for line in lines
        if (rule := _parse_line(str(line)))
    ]


def _normalise(value: Any) -> Any:
    if isinstance(value, list):
        return sorted(str(v) for v in value)

    if value is None:
        return None

    return str(value)


def _field_equal(
    actual: dict[str, Any],
    desired: dict[str, Any],
    field: str,
) -> bool:

    if field not in desired:
        return True

    if field not in actual:
        return False

    actual_value = actual[field]

    if field == "connection-state":
        actual_value = actual_value.split(",")

    return (
        _normalise(actual_value)
        == _normalise(desired[field])
    )

def evaluate_firewall_order(current_rules, baseline):
    comment_to_name = {
        item["comment"]: item["name"]
        for item in baseline
    }

    desired_by_chain = {}
    for item in baseline:
        desired_by_chain.setdefault(item["chain"], []).append(item["name"])

    actual_by_chain = {}
    for rule in current_rules:
        comment = rule.get("comment")
        name = comment_to_name.get(comment)

        if name is None:
            continue

        chain = rule.get("chain")
        if chain is None:
            continue

        actual_by_chain.setdefault(chain, []).append(name)

    order_drift = []
    order_results = []

    for chain, desired_order in desired_by_chain.items():
        actual_order = actual_by_chain.get(chain, [])

        if len(actual_order) != len(desired_order):
            order_results.append({
                "chain": chain,
                "status": "UNDETERMINED",
                "desired": desired_order,
                "actual": actual_order,
            })
            continue

        if actual_order == desired_order:
            order_results.append({
                "chain": chain,
                "status": "COMPLIANT",
                "desired": desired_order,
                "actual": actual_order,
                "drifted": [],
            })
            continue

        # Report drifted rules in desired-state order.
        drifted = [
            name
            for index, name in enumerate(desired_order)
            if actual_order[index] != name
        ]

        order_drift.extend(drifted)

        order_results.append({
            "chain": chain,
            "status": "ORDER_DRIFT",
            "desired": desired_order,
            "actual": actual_order,
            "drifted": drifted,
        })

    return {
        "order_drift": order_drift,
        "order_results": order_results,
    }
    comment_to_name = {
        item["comment"]: item["name"]
        for item in baseline
    }

    desired_by_chain = {}
    for item in baseline:
        desired_by_chain.setdefault(item["chain"], []).append(item["name"])

    actual_by_chain = {}
    for rule in current_rules:
        comment = rule.get("comment")
        name = comment_to_name.get(comment)

        if name is None:
            continue

        chain = rule.get("chain")
        if chain is None:
            continue

        actual_by_chain.setdefault(chain, []).append(name)

    order_drift = []
    order_results = []

    for chain, desired_order in desired_by_chain.items():
        actual_order = actual_by_chain.get(chain, [])

        if len(actual_order) != len(desired_order):
            order_results.append({
                "chain": chain,
                "status": "UNDETERMINED",
                "desired": desired_order,
                "actual": actual_order,
            })
            continue

        if actual_order == desired_order:
            order_results.append({
                "chain": chain,
                "status": "COMPLIANT",
                "desired": desired_order,
                "actual": actual_order,
            })
            continue

        # Detect only rules whose relative position differs
        # from the desired managed-rule order.
        drifted = []

        for index, name in enumerate(actual_order):
            if name != desired_order[index]:
                drifted.append(name)

        order_drift.extend(drifted)

        order_results.append({
            "chain": chain,
            "status": "ORDER_DRIFT",
            "desired": desired_order,
            "actual": actual_order,
            "drifted": drifted,
        })

    return {
        "order_drift": order_drift,
        "order_results": order_results,
    }

def evaluate_firewall_baseline(
    current_rules: list[dict[str, Any]],
    baseline: list[dict[str, Any]],
) -> dict[str, Any]:

    results = []

    missing = []
    disabled = []
    duplicate = []
    drift = []
    compliant = []

    managed_fields = [
        "chain",
        "action",
        "connection-state",
        "in-interface",
        "out-interface",
        "protocol",
        "src-address",
        "dst-address",
        "src-port",
        "dst-port",
    ]

    for desired in baseline:

        name = desired["name"]
        comment = desired["comment"]

        matches = [
            rule
            for rule in current_rules
            if rule.get("comment") == comment
        ]

        result = {
            "name": name,
            "comment": comment,
            "status": "COMPLIANT",
        }

        if not matches:
            result["status"] = "MISSING"
            missing.append(name)
            results.append(result)
            continue

        if len(matches) > 1:
            result["status"] = "DUPLICATE"
            result["count"] = len(matches)
            duplicate.append(name)
            results.append(result)
            continue

        actual = matches[0]

        if actual.get("_disabled"):
            result["status"] = "DISABLED"
            disabled.append(name)
            results.append(result)
            continue

        mismatches = [
            field
            for field in managed_fields
            if not _field_equal(
                actual,
                desired,
                field,
            )
        ]

        if mismatches:
            result["status"] = "DRIFT"
            result["fields"] = mismatches
            drift.append(name)
        else:
            compliant.append(name)

        results.append(result)

    order = evaluate_firewall_order(
        current_rules,
        baseline,
    )

    return {
        "results": results,
        "missing": missing,
        "disabled": disabled,
        "duplicate": duplicate,
        "drift": drift,
        "compliant": compliant,
        "order_drift": order["order_drift"],
        "order_results": order["order_results"],
        "compliant_count": len(compliant),
        "managed_count": len(baseline),
    }


class FilterModule(object):
    """Ansible filter plugin entry point."""

    def filters(self):
        return {
            "routeros_parse_rules": parse_routeros_rules,
            "routeros_firewall_compliance":
                evaluate_firewall_baseline,
        }