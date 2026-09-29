Ansible Network Configuration & Compliance Automation

An Ansible-based network automation project for managing, validating, and enforcing configuration state on MikroTik RouterOS through SSH.

This project was built and validated against a real MikroTik RouterOS environment and is being developed incrementally toward a broader multi-device, multi-vendor network configuration and compliance framework.

The project is intentionally versioned: each release adds a defined layer of automation capability while keeping the existing workflow testable and operational.

---

Project Overview

The core idea is simple:

Desired State
     ↓
Collect Current State
     ↓
Normalize / Compare
     ↓
Detect Drift
   ↙       ↘
Match      Drift
  ↓          ↓
Compliant  Remediate
             ↓
          Validate
             ↓
          Compliant

The project focuses on the operational lifecycle of network configuration:

Define → Observe → Compare → Detect → Remediate → Validate → Report

Rather than treating network automation as a collection of device commands, the project uses a desired-state approach where configuration changes are conditional, validated, and designed to be repeatable.

---

Project Objective

The objective is to demonstrate practical Network Automation and Configuration Management capabilities using technologies that are relevant to real network infrastructure environments.

The current implementation demonstrates:

- Desired-state configuration
- Network device automation
- Idempotent configuration changes
- Configuration drift detection
- Automated remediation
- Post-change validation
- SSH-based network management
- Ansible Network CLI
- MikroTik RouterOS automation
- Python-based validation and remediation
- Reproducible dependency management
- Operational troubleshooting
- Separation of automation logic from environment-specific credentials

The project is intentionally being developed in stages rather than claiming capabilities that have not yet been implemented.

---

Current Scope

The current release is focused on a real MikroTik RouterOS environment.

Current compliance control

Device Platform:
MikroTik RouterOS

Compliance Control:
RouterOS system identity

Desired State:
AnsibleMikrotik

The current workflow performs:

1. Connect to the RouterOS device over SSH
2. Collect the current device state
3. Normalize the returned CLI output
4. Compare actual state with desired state
5. Apply a change only when required
6. Collect the state again
7. Validate the resulting configuration
8. Report the compliance result

The current release deliberately does not claim multi-device or multi-vendor production support.

Those capabilities are part of the planned development roadmap.

---

Real-World Validation

The automation workflow has been exercised against a real MikroTik RouterOS environment.

The implementation was not designed only as a theoretical Ansible example. The project has been used to investigate actual network-device automation behavior, including SSH connectivity, Ansible Network CLI behavior, vendor collection behavior, persistent connections, and RouterOS-specific constraints.

This provides a practical foundation for extending the project into additional compliance controls and eventually additional network platforms.

---

A Real Network Automation Troubleshooting Case

During development, "community.routeros.command" produced repeated SSH command timeouts even though lower-level SSH connectivity and other Ansible connectivity tests were working.

The investigation covered the complete automation chain:

- Direct SSH connectivity
- Ansible "network_cli"
- "libssh"
- Persistent connection state
- Ansible collections
- RouterOS configuration
- Command execution behavior

The verified trigger in this environment was related to the RouterOS system identity used by the SSH-based Ansible workflow.

The Ansible RouterOS SSH documentation specifies supported identity formatting and a maximum identity length of 19 characters.

The problematic identity exceeded that limit.

After changing the Rout

erOS identity to:

AnsibleMikrotik

the same automation executed successfully without changing the playbook logic.

This troubleshooting case is an important part of the project because it demonstrates that network-automation failures must be investigated across the complete chain:

Network Device
      ↓
SSH
      ↓
Connection Plugin
      ↓
Ansible
      ↓
Vendor Collection
      ↓
Command Execution

A timeout is not necessarily a playbook problem.

---

Automation Architecture

The primary configuration workflow is implemented in:

ansible/configure_router.yml

Supporting Python utilities:

scripts/validate_mikrotik.py
scripts/remediate_mikrotik.py

Ansible

Ansible is responsible for:

- Desired-state configuration
- Conditional configuration changes
- Network-device automation
- Idempotent execution
- Post-change validation
- Compliance workflow

Python

Python provides complementary utilities for:

- State validation
- Drift detection
- Independent remediation
- Custom automation logic
- Future integrations

This separation keeps the main network configuration workflow in Ansible while allowing Python to handle supporting automation and custom logic.

---

Repository Structure

.
├── ansible/
│   ├── configure_router.yml
│   └── inventory.example.ini
├── scripts/
│   ├── validate_mikrotik.py
│   └── remediate_mikrotik.py
├── .gitignore
├── ansible.cfg
├── requirements.yml
└── README.md

The real local inventory is intentionally excluded from version control because it can contain environment-specific connection information and credentials.

---

Technology Stack

The repository is designed around reproducible dependency versions.

Component| Version
Ansible Core| 2.21.4
Python| 3.14.4
ansible.netcommon| 8.7.1
community.routeros| 3.22.0
MikroTik RouterOS| 7.x
Connection| SSH / Network CLI

The repository's "requirements.yml" is the source of truth for the Ansible collection versions used for reproducible installation.

The RouterOS automation uses:

ansible.netcommon.network_cli
community.routeros
SSH / libssh

---

Installation

Install the required Ansible collections:

ansible-galaxy collection install -r requirements.yml

Verify the installed collections if required:

ansible-galaxy collection list

---

Configuration

Create a local inventory from the example:

cp ansible/inventory.example.ini ansible/inventory.local.ini

Edit:

ansible/inventory.local.ini

and provide the connection information for the target RouterOS device.

The local inventory is excluded from Git.

For real deployments, credentials should preferably be managed using mechanisms such as:

- SSH keys
- Ansible Vault
- Environment variables
- Dedicated secrets-management systems

---

Running the Automation

Run the configuration workflow with:

ansible-playbook \
  -i ansible/inventory.local.ini \
  ansible/configure_router.yml

The playbook performs:

1. Current-state collection
2. Output normalization
3. Desired-state comparison
4. Conditional remediation
5. Post-change state collection
6. Explicit validation
7. Compliance reporting

---

Idempotency

Idempotency is a core design requirement.

If the device already matches the desired state, the configuration task should not make an unnecessary configuration change.

Conceptually:

First run with drift:

Actual
  ↓
Mismatch
  ↓
Change
  ↓
Validate
  ↓
Compliant

A subsequent execution:

Actual
  ↓
Match
  ↓
No configuration change
  ↓
Validate
  ↓
Compliant

This allows the automation to be executed repeatedly without unnecessarily modifying an already-compliant device.

The repository deliberately avoids publishing a fixed Ansible task recap such as "ok=..." because task counts may change as the implementation evolves.

The important result is the behavior of the automation, not a hard-coded execution summary.

---

Configuration Drift

Configuration drift is treated as an explicit operational state.

Desired State
     ↓
   Compare
   ↙     ↘
Match   Mismatch
  ↓        ↓
Clean   Remediate
           ↓
        Validate
           ↓
         Clean

The same model can later be extended to ad

ditional controls such as:

- Firewall policy
- Management services
- NTP
- DNS
- Interface configuration
- Routing policy
- Security hardening
- Access controls

---

Python Validation

The validation utility can be executed independently of the Ansible workflow.

Set the required connection parameters:

export MIKROTIK_HOST="YOUR_SERVER_IP"
export MIKROTIK_PORT="2222"
export MIKROTIK_USER="admin"

Run:

python3 scripts/validate_mikrotik.py

The validation utility reports:

- Desired state
- Actual state
- Drift status

The validation script is read-only and does not modify the device.

---

Python Remediation

When configuration drift is detected, the remediation utility can be executed:

python3 scripts/remediate_mikrotik.py

Then validate the resulting state:

python3 scripts/validate_mikrotik.py

This provides an independent:

Detect → Remediate → Validate

workflow alongside the main Ansible configuration path.

---

MikroTik SSH Compatibility

The tested RouterOS environment required specific SSH terminal compatibility settings.

The effective SSH username used in the tested environment included:

admin+cet512w

The Network CLI connection used:

ansible_network_cli_ssh_type=libssh

The "+cet..." username suffix and terminal-detection behavior are environment-specific and should not be assumed to be mandatory for every RouterOS deployment.

These details are documented because they were relevant to the real environment in which the automation was tested.

---

Security

The repository must not contain sensitive environment data.

Never commit:

- Passwords
- Private SSH keys
- API tokens
- Production inventories
- Configuration backups containing secrets
- ".env" files
- Vault passwords

The ".gitignore" excludes the local inventory and generated network data.

The public repository contains the automation logic and reproducible project structure, while environment-specific secrets remain outside version control.

---

Development Roadmap

The project is intentionally designed as a multi-version development effort.

The current MikroTik implementation is the foundation, not the final scope.

Each future version is intended to extend the same core model:

Desired State
      ↓
Detect Drift
      ↓
Remediate
      ↓
Validate
      ↓
Report

---

v1.0 — RouterOS Configuration & Compliance Foundation

Current release

Implemented capabilities:

- Ansible Network CLI
- SSH-based MikroTik management
- "community.routeros"
- Desired-state configuration
- Idempotent execution
- Configuration drift detection
- Conditional remediation
- Post-change validation
- Python validation
- Python remediation
- Real-world troubleshooting documentation
- Secure separation of local credentials and public automation code

Current compliance control:

RouterOS System Identity
Desired value: AnsibleMikrotik

---

v1.1 — Extended MikroTik Compliance

The next stage will expand the number of compliance controls implemented for RouterOS.

Planned areas include:

- Firewall compliance
- Management-service hardening
- NTP configuration
- DNS configuration
- Interface configuration
- Additional security-hardening policies
- Expanded drift detection
- Compliance reporting

The goal is to move from a single compliance control toward a reusable RouterOS compliance baseline.

---

v1.2 — Automation Engineering & CI

After expanding the compliance model, the project will add stronger engineering and quality controls.

Planned capabilities include:

- Ansible linting
- Automated syntax validation
- Regression checks
- Structured compliance reports
- GitHub Actions
- Automated validation in CI
- Improved testability of automation logic

The objective is to make the automation more reproducible and maintainable as the project grows.

---

v2.0 — Multi-Device Automation

After the RouterOS compliance model is stable, the project will expand from a single managed device to multiple devices.

Planned capabilities include:

- Multiple MikroTik devices
- Standardized inventories
- Device groups
- Group-based configuration
- Configuration baselines
- Multi-de

vice compliance reporting
- Centralized drift visibility

The objective is to demonstrate that the automation model scales beyond a single device.

---

v2.x — Multi-Vendor Network Automation

The next major expansion is to additional network platforms.

Cisco IOS and FortiGate are planned targets.

The project will investigate how the same desired-state and compliance model can be applied across different vendors while keeping vendor-specific implementation details separated where necessary.

Planned platforms:

MikroTik RouterOS
       ↓
Cisco IOS
       ↓
FortiGate

The goal is to evolve the project into a reusable multi-vendor network configuration and compliance framework.

---

Future Direction

As the multi-vendor automation foundation becomes mature, the project can be extended toward:

- Git-based change management
- CI/CD
- Network APIs
- Automated compliance reporting
- Infrastructure as Code practices
- Cloud networking integration
- Network monitoring integration
- Configuration backup and recovery
- Automated operational workflows

These capabilities will be added only when they provide a meaningful extension to the project rather than being added as unrelated technologies.

---

Design Principles

Reproducible

Dependencies are explicitly defined and the project provides an example inventory.

Idempotent

Configuration changes are conditional on the difference between actual and desired state.

Validated

Configuration changes are followed by explicit state validation.

Operationally Tested

The workflow has been exercised against a real MikroTik RouterOS environment.

Troubleshootable

The project documents a real automation failure and the end-to-end investigation used to identify the device-side constraint.

Extensible

New compliance controls and network platforms can follow the same desired-state, remediation, and validation model.

Secure

Environment-specific credentials and sensitive data remain outside version control.

Incremental

The project is developed through defined versions rather than claiming capabilities before they are implemented and validated.

---

Project Status

Version:               1.0
Status:                Implemented and validated
Environment:           Real MikroTik RouterOS
Primary automation:    Ansible
Supporting automation: Python
Management protocol:   SSH

Current control:
RouterOS System Identity

Current focus:
Configuration Management
Compliance
Drift Detection
Remediation
Validation

Planned expansion:
Extended RouterOS Compliance
CI / Automation Quality
Multi-Device Automation
Cisco IOS
FortiGate
Multi-Vendor Network Automation

---

Project Evolution

v1.0
MikroTik Foundation
      ↓
v1.1
Extended Compliance
      ↓
v1.2
Automation Quality / CI
      ↓
v2.0
Multi-Device
      ↓
v2.x
Cisco + FortiGate
      ↓
Multi-Vendor Network Automation

The project is developed incrementally, and each new capability is added after implementation and validation.