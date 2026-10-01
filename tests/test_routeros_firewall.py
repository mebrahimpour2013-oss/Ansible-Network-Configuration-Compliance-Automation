from filter_plugins.routeros_firewall import (
    evaluate_firewall_baseline,
    parse_routeros_rules,
)


BASELINE = [
    {
        "name": "allow-established-forward",
        "comment": "allow-established-forward",
        "chain": "forward",
        "action": "accept",
        "connection-state": ["established", "related"],
    },
    {
        "name": "drop-invalid-forward",
        "comment": "drop-invalid-forward",
        "chain": "forward",
        "action": "drop",
        "connection-state": ["invalid"],
    },
    {
        "name": "drop-new-forward",
        "comment": "drop-new-forward",
        "chain": "forward",
        "action": "drop",
        "connection-state": ["new"],
    },
]


CLEAN = [
    (
        "0 comment=allow-established-forward "
        "chain=forward action=accept "
        "connection-state=established,related"
    ),
    (
        "1 comment=drop-invalid-forward "
        "chain=forward action=drop "
        "connection-state=invalid"
    ),
    (
        "2 comment=drop-new-forward "
        "chain=forward action=drop "
        "connection-state=new"
    ),
]


def test_parser_handles_routeros_terse_output():
    rules = parse_routeros_rules(CLEAN)

    assert rules[0]["comment"] == "allow-established-forward"
    assert rules[1]["comment"] == "drop-invalid-forward"
    assert rules[2]["comment"] == "drop-new-forward"


def test_clean_state_is_compliant():
    result = evaluate_firewall_baseline(
        parse_routeros_rules(CLEAN),
        BASELINE,
    )

    assert result["compliant"] == [
        "allow-established-forward",
        "drop-invalid-forward",
        "drop-new-forward",
    ]

    assert result["missing"] == []
    assert result["disabled"] == []
    assert result["drift"] == []
    assert result["duplicate"] == []
    assert result["order_drift"] == []


def test_disabled_rule_is_detected():
    lines = [
        (
            "0 comment=allow-established-forward "
            "chain=forward action=accept "
            "connection-state=established,related"
        ),
        (
            "X 1 comment=drop-invalid-forward "
            "chain=forward action=drop "
            "connection-state=invalid"
        ),
        (
            "2 comment=drop-new-forward "
            "chain=forward action=drop "
            "connection-state=new"
        ),
    ]

    result = evaluate_firewall_baseline(
        parse_routeros_rules(lines),
        BASELINE,
    )

    assert result["disabled"] == ["drop-invalid-forward"]


def test_missing_rule_is_detected():
    result = evaluate_firewall_baseline(
        parse_routeros_rules(
            [
                CLEAN[0],
                CLEAN[2],
            ]
        ),
        BASELINE,
    )

    assert result["missing"] == ["drop-invalid-forward"]


def test_field_drift_is_detected():
    lines = [
        CLEAN[0],
        (
            "1 comment=drop-invalid-forward "
            "chain=forward action=accept "
            "connection-state=invalid"
        ),
        CLEAN[2],
    ]

    result = evaluate_firewall_baseline(
        parse_routeros_rules(lines),
        BASELINE,
    )

    assert result["drift"] == ["drop-invalid-forward"]


def test_duplicate_control_is_detected():
    lines = CLEAN + [
        (
            "3 comment=drop-new-forward "
            "chain=forward action=drop "
            "connection-state=new"
        )
    ]

    result = evaluate_firewall_baseline(
        parse_routeros_rules(lines),
        BASELINE,
    )

    assert result["duplicate"] == ["drop-new-forward"]


def test_order_drift_is_detected():
    lines = [
        CLEAN[0],
        CLEAN[2],
        CLEAN[1],
    ]

    result = evaluate_firewall_baseline(
        parse_routeros_rules(lines),
        BASELINE,
    )

    assert result["order_drift"] == [
        "drop-invalid-forward",
        "drop-new-forward",
    ]

    assert result["order_results"][0]["status"] == "ORDER_DRIFT"
def test_environment_rules_are_ignored_for_order():
    lines = [
        CLEAN[0],
        (
            "1 comment=SSTP VPN to Internet "
            "chain=forward action=accept "
            "src-address=10.20.20.0/24 "
            "out-interface=ether1"
        ),
        CLEAN[1],
        (
            "3 comment=allow ICMP "
            "chain=input action=accept protocol=icmp"
        ),
        CLEAN[2],
    ]

    result = evaluate_firewall_baseline(
        parse_routeros_rules(lines),
        BASELINE,
    )

    assert result["order_drift"] == []