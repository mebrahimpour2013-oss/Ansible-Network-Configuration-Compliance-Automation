# Ansible Network Configuration & Compliance Automation

Business-oriented network configuration governance and compliance automation for MikroTik RouterOS.

This project implements a declarative configuration-compliance workflow for network infrastructure using Ansible, a custom RouterOS parser/compliance engine, automated remediation, post-change validation, and CI-based quality checks.

The implementation was developed and validated against a real MikroTik RouterOS environment rather than being limited to a simulated or purely theoretical lab scenario.

---

## Project Purpose

Network devices tend to accumulate configuration drift over time.

Manual configuration changes, troubleshooting, emergency changes, and different administrative practices can cause a device's actual configuration to diverge from the organization's intended state.

This project addresses that problem by treating selected network controls as a desired state and continuously comparing the actual device configuration against that state.

The workflow is:
```text
Desired Configuration
        |
        v
Collect Device State
        |
        v
Parse RouterOS Configuration
        |
        v
Compliance Evaluation
        |
        +-------------------+
        |                   |
     COMPLIANT             DRIFT
        |                   |
        |        +----------+----------+
        |        |          |          |
        |      Missing   Disabled   Field/Order
        |                            Drift
        |        +----------+----------+
        |                   |
        |                   v
        |            Ansible Remediation
        |                   |
        |                   v
        +---------- Post-Change Validation
                            |
                            v
                       COMPLIANT
```

The goal is not simply to configure a router.

The goal is to establish a repeatable configuration governance and compliance process that can be extended to larger network environments.


---

Current Implementation

The current implementation manages a declarative firewall baseline for MikroTik RouterOS.

The baseline currently contains six managed controls:

1. Accept established/related input traffic


2. Drop invalid input traffic


3. Accept established/related forward traffic


4. Drop invalid forward traffic


5. Drop WAN input traffic


6. Drop new WAN forward traffic



Environment-specific controls remain outside the managed baseline.

Examples include:

SSTP VPN access

VPN management access

QEMU-forwarded SSH access

QEMU-forwarded Winbox access

ICMP access


This separation is intentional.

The automation does not attempt to take ownership of every existing firewall rule. It manages only controls explicitly defined in the desired-state baseline.


---

Key Capabilities

Declarative Desired State

The intended configuration is defined as structured YAML rather than being embedded inside remediation code.

Example:

firewall_baseline:
  - name: allow-established-related-input
    chain: input
    action: accept
    connection-state:
      - established
      - related

This makes the desired configuration reviewable, versionable, and suitable for future multi-device governance.


---

Structured RouterOS Parsing

RouterOS firewall output is collected using the RouterOS CLI and parsed into structured data through a custom Ansible filter plugin.

The parser provides a consistent representation of firewall rules for compliance evaluation.

The compliance engine does not depend on fragile standalone regular-expression checks.


---

Compliance Detection

The implementation detects:

Missing controls

Disabled controls

Field-level configuration drift

Duplicate managed controls

Managed rule order drift

Overall baseline compliance


The compliance engine evaluates the actual matched rule rather than allowing different rules to satisfy different portions of a desired control.


---

Safe Remediation

Detected drift can be remediated through Ansible.

The remediation workflow can:

Enable disabled managed rules

Correct field-level drift

Create missing rules

Position newly created rules appropriately

Correct managed rule ordering

Refuse ambiguous duplicate controls instead of modifying an arbitrary rule


Duplicate managed controls are treated as an unsafe condition.

Instead of guessing which rule should be modified, the automation fails safely and requires the ambiguity to be resolved.


---

Managed Rule Ordering

Firewall rule order is part of the compliance model.

For managed controls within the same RouterOS chain, the automation verifies the desired relative order and can remediate order drift.

Environment-specific rules are intentionally ignored when calculating managed order.

This prevents unrelated infrastructure-specific rules from affecting the compliance result.


---

Post-Remediation Validation

Remediation is not considered successful merely because an Ansible task reports changed.

The device state is collected again after remediation and evaluated against the desired baseline.

The final state must satisfy the compliance engine.

Expected result:

FIREWALL BASELINE: COMPLIANT


---

Idempotent Execution

The automation is designed to be idempotent.

If the device already matches the desired state, running the playbook again should not make unnecessary changes.

A clean-state execution has been verified with:

changed=0
failed=0
FIREWALL BASELINE: COMPLIANT


---

Real-Environment Validation

The implementation has been exercised against a MikroTik RouterOS 7.23.7 CHR environment using Ansible Network CLI over SSH.

The environment includes:

MikroTik RouterOS 7.23.7

QEMU CHR

SSH connectivity

Ansible network_cli

community.routeros

ansible.netcommon


The firewall baseline was tested through actual device configuration changes.

Validation included:

Clean baseline detection

Disabled-rule remediation

Missing-rule handling

Field-level drift remediation

Duplicate-rule safety handling

Firewall order drift detection

Firewall order remediation

Post-remediation validation

Idempotent re-execution


The rule-order remediation was also tested by intentionally introducing order drift on the device and verifying that the automation detected and corrected it.


---

Architecture

Git Repository
                          |
                          v
                 Desired State YAML
                          |
                          v
              Ansible Remediation Playbook
                          |
                          v
                RouterOS Network CLI
                          |
                          v
                  MikroTik RouterOS
                          |
                          v
                Actual Device State
                          |
                          v
              RouterOS Filter Plugin
                          |
                          v
                Compliance Evaluation
                          |
                 +--------+--------+
                 |                 |
              COMPLIANT          DRIFT
                                   |
                                   v
                           Ansible Remediation
                                   |
                                   v
                          Post-Change Validation
                                   |
                                   v
                              COMPLIANT

The architecture deliberately keeps the remediation engine in Ansible.

The custom Python-based component is implemented as an Ansible filter plugin responsible for parsing and compliance evaluation rather than acting as a second independent remediation system.


---

Repository Structure

.
├── .ansible-lint
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── README.md
├── ansible.cfg
├── ansible/
│   ├── group_vars/
│   │   └── routers.yml
│   ├── inventory.example.ini
│   └── remediate_firewall.yml
├── filter_plugins/
│   └── routeros_firewall.py
├── pytest.ini
├── requirements-dev.txt
├── requirements.yml
└── tests/
    └── test_routeros_firewall.py

Historical Python implementations are retained locally under _archive/ for reference and are intentionally excluded from the active repository architecture.


---

Requirements

Python 3.14.x

ansible-core 2.21.4

ansible.netcommon 8.7.1

community.routeros 3.22.0

RouterOS 7.x

SSH access to the target device

Ansible Network CLI

libssh support when configured through ansible_network_cli_ssh_type=libssh


Install Python development dependencies:

pip install -r requirements-dev.txt

Install required Ansible collections:

ansible-galaxy collection install -r requirements.yml


---

Inventory

A sanitized example inventory is provided:

ansible/inventory.example.ini

Create a local inventory from the example:

ansible/inventory.local.ini

The local inventory is excluded from Git.

Credentials must never be committed to the repository.

For production environments, use Ansible Vault or an external secret-management solution.


---

Running the Automation

Activate the Python environment:

source .venv/bin/activate

Run the remediation playbook:

ansible-playbook \
  -i ansible/inventory.local.ini \
  ansible/remediate_firewall.yml

A compliant device should report:

FIREWALL BASELINE: COMPLIANT

Running the playbook again without configuration changes should remain idempotent.


---

Compliance Model

Each managed control is identified by a stable logical name and matched using its desired configuration attributes.

The compliance engine evaluates:

Condition	Result

Control exists and matches desired state	COMPLIANT
Control is missing	MISSING
Control exists but is disabled	DISABLED
Managed fields differ	FIELD_DRIFT
Multiple matching managed controls exist	DUPLICATE
Managed order differs	ORDER_DRIFT


The final baseline result is compliant only when all managed controls satisfy the desired state.


---

Safety Boundaries

This project intentionally does not attempt to become a complete firewall-management platform.

It manages only controls explicitly declared in:

ansible/group_vars/routers.yml

Existing environment-specific rules are preserved.

The automation does not automatically delete arbitrary firewall rules.

Duplicate managed controls are not automatically resolved because doing so could result in modifying the wrong rule.

This conservative behavior is intentional for production-oriented configuration governance.


---

Testing

Unit Tests

Run:

pytest -q

The current test suite covers:

RouterOS rule parsing

Clean compliance

Disabled controls

Missing controls

Field drift

Duplicate controls

Rule-order drift

Ignoring environment-specific rules when evaluating managed order


Current validation:

8 passed


---

Ansible Syntax Validation

Run:

ansible-playbook \
  -i ansible/inventory.example.ini \
  ansible/remediate_firewall.yml \
  --syntax-check


---

Ansible Lint

Run:

ansible-lint ansible/remediate_firewall.yml

The project currently passes the Ansible Lint production profile with:

0 failure(s), 0 warning(s)


---

Continuous Integration

GitHub Actions validates the project automatically.

The CI workflow performs:

1. Python environment setup


2. Dependency installation


3. Ansible collection installation


4. Unit tests


5. Ansible syntax validation


6. Ansible linting



The objective is to prevent invalid automation code from being merged into the project.


---

Project Design Principles

Infrastructure as Code

Desired network configuration is represented as version-controlled data.

Configuration Governance

The project focuses on maintaining an approved configuration state rather than performing one-time device configuration.

Idempotency

Repeated execution should converge the device toward the desired state without unnecessary changes.

Safe Failure

Ambiguous conditions such as duplicate managed controls are treated conservatively.

Separation of Concerns

Desired state, parsing, compliance evaluation, remediation, and validation have distinct responsibilities.

Vendor-Aware Implementation

The current implementation targets MikroTik RouterOS while keeping the governance workflow suitable for future multi-vendor expansion.

Production-Oriented Development

The implementation has been exercised against an actual RouterOS environment and includes both functional testing and automated code-quality validation.


---

Roadmap

v1.1 — Extended MikroTik Compliance

Potential extensions include:

Management-plane hardening

NTP baseline

DNS baseline

Interface hardening

Additional firewall controls

Expanded compliance reporting

More detailed drift reporting


v1.2 — Configuration Governance

Potential extensions include:

Pull-request driven configuration review

Change approval workflow

Compliance reports

Configuration snapshots

Historical drift tracking


v2.0 — Multi-Device

Potential extensions include:

Multiple MikroTik devices

Device groups

Site-specific desired state

Per-device variables

Centralized compliance reporting


v2.x — Multi-Vendor

Extend the governance model to additional network platforms while keeping the compliance workflow and operational principles consistent.

Potential targets may include:

Cisco IOS / IOS-XE

FortiGate

Other platforms supported by Ansible Network Collections



---

Project Status

Current status: v1.0 — MikroTik Firewall Configuration Compliance

Implemented and validated:

Declarative firewall baseline

RouterOS structured parsing

Compliance evaluation

Missing-rule detection

Disabled-rule detection

Field drift detection

Duplicate detection

Managed order drift detection

Automated remediation

Post-remediation validation

Idempotent execution

Unit testing

Ansible syntax validation

Production-profile Ansible linting

CI workflow

Real RouterOS environment validation


The current implementation provides the foundation for expanding the project from single-device firewall compliance into broader network configuration governance and eventually multi-device / multi-vendor Network DevOps.
