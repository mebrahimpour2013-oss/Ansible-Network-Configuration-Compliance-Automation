Ansible Network Configuration & Compliance Automation

Ansible-based network automation project for managing and validating MikroTik RouterOS configuration through SSH.

This repository was built and validated against a real MikroTik RouterOS environment. It is intentionally focused on a small, testable compliance control rather than pretending to be a complete multi-vendor platform.

The core operational workflow is:

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

Project Objective

The goal is to demonstrate practical network-engineering automation:

- define a desired device state
- detect configuration drift
- change configuration only when required
- validate the resulting state
- keep environment-specific credentials outside Git
- provide a foundation for additional compliance policies

Ansible is the primary configuration-management layer. Python provides complementary validation and remediation utilities.

What This Project Demonstrates

- Network automation
- Ansible Network CLI
- MikroTik RouterOS automation
- SSH-based device management
- Desired-state configuration
- Idempotency
- Configuration drift detection
- Automated remediation
- Post-change validation
- Python automation
- Reproducible configuration
- Troubleshooting across the device/SSH/Ansible/vendor-collection stack

Real-World Validation

The current implementation was executed against a real MikroTik RouterOS environment.

Current compliance policy:

RouterOS system identity
Desired value: AnsibleMikrotik

The complete workflow has been exercised:

1. connect to RouterOS over SSH
2. read the current identity
3. normalize the CLI output
4. compare actual vs desired state
5. change the identity only when drift exists
6. read the state again
7. validate the resulting state
8. report compliance

The current release deliberately does not claim multi-device or multi-vendor production support. The architecture is designed so those capabilities can be added after the single-device workflow is proven.

A Real Troubleshooting Case

During development, "community.routeros.command" produced repeated SSH command timeouts even though lower-level SSH connectivity and other Ansible connectivity tests were working.

The investigation checked:

- direct SSH connectivity
- "network_cli"
- "libssh"
- persistent connection state
- Ansible collections
- RouterOS configuration
- command execution behavior

The verified trigger in this environment was the RouterOS system identity used by the SSH-based Ansible workflow.

The Ansible RouterOS SSH guide documents that the identity should use supported characters and must not exceed 19 characters.

After changing the identity to:

AnsibleMikrotik

the same automation executed successfully without changing the playbook logic.

This makes the project more than a playbook example: it also records a real network-automation troubleshooting case.

Automation Architecture

The Ansible workflow is implemented in:

ansible/configure_router.yml

Supporting utilities:

scripts/validate_mikrotik.py
scripts/remediate_mikrotik.py

The intended separation is:

Ansible

- desired-state configuration
- idempotent changes
- network-device automation
- compliance workflow

Python

- lightweight state validation
- drift detection
- remediation utility
- future integrations/custom logic

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

The real local inventory is intentionally excluded from version control.

Technology Stack

The repository is pinned to these reproducible dependency versions:

Component| Version
Ansible Core| 2.21.4
Python| 3.14.4
ansible.netcommon| 8.7.1
community.routeros| 3.9.0
MikroTik RouterOS| 7.x
Connection| SSH / Network CLI

The repository's "requirements.yml"

is the source of truth for the collection versions used for reproducible installation.

The RouterOS command module uses "ansible.netcommon.network_cli" with the "community.routeros" collection.

Installation

Install the required collections:

ansible-galaxy collection install -r requirements.yml

Verify them if required:

ansible-galaxy collection list

Configuration

Create a local inventory:

cp ansible/inventory.example.ini ansible/inventory.local.ini

Edit:

ansible/inventory.local.ini

with the connection information for the target RouterOS device.

The local inventory is excluded from Git because it can contain credentials and environment-specific information.

For real deployments, prefer:

- SSH keys
- Ansible Vault
- environment variables
- a dedicated secrets-management system

Running the Automation

ansible-playbook \
  -i ansible/inventory.local.ini \
  ansible/configure_router.yml

The playbook performs:

1. current-state collection
2. output normalization
3. desired-state comparison
4. conditional remediation
5. post-change collection
6. explicit validation
7. compliance reporting

Idempotency

Idempotency is a core requirement.

When the device already matches the desired state, the configuration task should not make another configuration change.

Conceptually:

First run with drift:
Actual → Mismatch → Change → Validate → Compliant

Later run:
Actual → Match → No change → Validate → Compliant

The repository avoids publishing a fixed Ansible recap such as "ok=..." because task counts can change as the playbook evolves.

The important behavioral result is that the desired state is validated and repeated execution does not unnecessarily modify the device.

Configuration Drift

Drift is treated as an explicit operational state:

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

The same pattern can later be applied to:

- firewall policy
- management services
- NTP
- DNS
- interface configuration
- routing policy
- security hardening
- access controls

Python Validation

The read-only validation utility can be used independently of the Ansible playbook.

Set the connection parameters:

export MIKROTIK_HOST="YOUR_SERVER_IP"
export MIKROTIK_PORT="2222"
export MIKROTIK_USER="admin"

Run:

python3 scripts/validate_mikrotik.py

A compliant device reports the desired identity, actual identity, and a clean drift status.

The validation script does not modify the device.

Python Remediation

When drift is detected:

python3 scripts/remediate_mikrotik.py

Validate again:

python3 scripts/validate_mikrotik.py

This provides a simple:

Detect → Remediate → Validate

workflow outside the main Ansible execution path.

MikroTik SSH Compatibility

The tested RouterOS environment required specific SSH terminal compatibility settings.

The effective SSH username uses:

admin+cet512w

and the Network CLI connection uses:

ansible_network_cli_ssh_type=libssh

The "+cet..." username suffix and terminal-detection behavior are environment-specific and should not be assumed to be mandatory for every RouterOS deployment.

Security

Never commit:

- passwords
- private SSH keys
- API tokens
- production inventories
- configuration backups containing secrets
- ".env" files
- Vault passwords

The repository's ".gitignore" excludes the local inventory and generated network data.

The public repository contains the automation logic and reproducible project structure, while environment-specific secrets remain outside version control.

Design Principles

Reproducible

Dependencies are defined in "requirements.yml" and an example inventory is provided.

Idempotent

Changes are conditional on the difference between actual and desired state.

Validated

The resulting device state is explicitly checked after a configuration operation.

Operationally Tested

The workflow has been exercised against a real MikroTik RouterOS environment.

Troubleshootable

The repository documents an actual automation timeout and the end-to-end investigation tha

t identified the device-side constraint.

Extensible

Additional compliance controls can use the same desired-state → remediation → validation architecture.

Secure

Credentials and environment-specific data remain outside version control.

Roadmap

The roadmap is deliberately incremental and aligned with real network-automation work.

v1.1 — Extended RouterOS Compliance

Planned controls:

- firewall compliance
- management-service hardening
- NTP configuration
- DNS configuration
- interface configuration
- additional security policies
- drift reporting

v1.2 — Automation Quality

Planned engineering improvements:

- Ansible linting
- automated syntax validation
- structured compliance reports
- GitHub Actions
- automated regression checks

v2.x — Multi-Device / Multi-Vendor

After the RouterOS compliance model is stable, expand to multiple devices and eventually other platforms such as Cisco.

The goal is not a collection of unrelated device scripts.

The goal is a reusable network configuration and compliance framework.

Project Status

Version:               1.0
Status:                Implemented and validated
Environment:           Real MikroTik RouterOS
Primary automation:    Ansible
Supporting automation: Python
Management protocol:   SSH
Current control:       RouterOS system identity
Focus:                 Configuration Management
                       Compliance
                       Drift Detection
                       Remediation
                       Validation

Why This Project Matters

This is intentionally positioned as a network-engineering automation project, not an Ansible syntax exercise.

It demonstrates the complete operational loop:

Define
  ↓
Observe
  ↓
Compare
  ↓
Detect Drift
  ↓
Remediate
  ↓
Validate
  ↓
Report

It also demonstrates an important practical skill: troubleshooting the complete automation chain rather than assuming that every timeout is a playbook problem.

This is the foundation for the next stages of the project: broader compliance policies, multi-device automation, reporting, CI/CD, and eventually multi-vendor network automation.

License

No open-source license has been selected for the initial release.

A license can be added if the project is later intended for public reuse, redistribution, or community contribution.