Ansible Network Configuration & Compliance Automation

Ansible-based network automation project for managing and validating MikroTik RouterOS configuration through SSH.

The project implements a practical configuration management and compliance workflow that detects configuration drift, applies the required remediation, and validates the resulting device state.

The solution has been implemented and validated against a real MikroTik RouterOS environment.

---

Overview

Maintaining consistent configurations across network devices is an important part of network operations and security.

Manual configuration makes it difficult to maintain consistency, detect unauthorized or accidental changes, and verify that devices remain in their intended state.

This project addresses that problem by defining a desired configuration state and automating the process of:

Current State
      ↓
State Comparison
      ↓
Drift Detection
      ↓
Remediation
      ↓
Validation
      ↓
Compliance Result

Ansible provides the primary configuration-management workflow, while Python scripts provide lightweight validation and remediation capabilities.

---

What This Project Demonstrates

The implementation demonstrates practical experience with:

- Network automation
- Ansible Network CLI
- MikroTik RouterOS automation
- SSH-based device management
- Configuration management
- Idempotent configuration changes
- Configuration drift detection
- Automated remediation
- Post-change validation
- Python network automation
- Reproducible infrastructure configuration

---

Current Implementation

The current version manages and validates the MikroTik system identity:

AnsibleMikrotik

The scope is intentionally focused so that the underlying automation workflow remains clear and reliable.

The same architecture can subsequently be extended to additional configuration and compliance policies.

---

Automation Workflow

The Ansible playbook follows this process:

              ┌─────────────────┐
              │  RouterOS Device│
              └────────┬────────┘
                       │
                       ▼
              Read Current State
                       │
                       ▼
                Parse / Normalize
                       │
                       ▼
                Compare Desired
                       │
              ┌────────┴────────┐
              │                 │
          Compliant           Drift
              │                 │
              │                 ▼
              │             Remediate
              │                 │
              │                 ▼
              └────────► Validate
                                │
                                ▼
                       Compliance Result

This approach allows the same workflow to be reused as additional compliance controls are introduced.

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

---

Technology Stack

The implementation was developed and validated using:

Component| Version
Ansible Core| 2.21.4
Python| 3.14.4
ansible.netcommon| 8.7.1
community.routeros| 3.9.0
MikroTik RouterOS| 7.x
Connection| SSH / Network CLI

The tested versions are documented to make the environment reproducible.

---

Installation

Install the required Ansible collections:

ansible-galaxy collection install -r requirements.yml

Verify the installed collections if required:

ansible-galaxy collection list

---

Configuration

Create a local inventory from the provided example:

cp ansible/inventory.example.ini ansible/inventory.local.ini

Edit:

ansible/inventory.local.ini

and configure the connection parameters for the target RouterOS device.

The local inventory is excluded from version control because it may contain environment-specific information and credentials.

For production environments, credentials should be managed through appropriate secret-management mechanisms such as:

- Ansible Vault
- SSH keys
- Environment variables
- Dedicated secrets-management systems

---

Running the Automation

Execute the configuration workflow with:

ansible-playbook \
  -i ansible/inventory.local.ini \
  ansible/configure_router.yml

The playbook:

1. Reads the current router identity.
2. Normalizes the RouterOS output.
3. Compares the current state with the desired state.
4. Changes the configuration only when required.
5. Reads the configuration again.
6. Validates the resulting state.
7. Reports the final compliance status.

---

Validation Result

The implementation was successfully executed against the target MikroTik RouterOS environment.

A compliant execution produced:

Router identity is compliant: AnsibleMikrotik

MikroTik configuration is compliant.

The validated baseline completed with:

ok=6
changed=0
unreachable=0
failed=0
skipped=1

The "changed=0" result demonstrates that the playbook does not make unnecessary configuration changes when the desired state is already present.

---

Configuration Drift

Configuration drift occurs when the actual state of a network device differs from its defined desired state.

This project treats drift as a manageable configuration state:

Desired State
      │
      ▼
   Compare
      │
 ┌────┴────┐
 │         │
Match    Mismatch
 │         │
 ▼         ▼
Compliant  Remediation
             │
             ▼
          Validation
             │
             ▼
          Compliant

This provides the foundation for implementing broader configuration-compliance policies without changing the overall architecture.

---

Python Validation

The project also includes a lightweight Python validation workflow.

Set the connection parameters:

export MIKROTIK_HOST="YOUR_SERVER_IP"
export MIKROTIK_PORT="2222"
export MIKROTIK_USER="admin"

Run:

python3 scripts/validate_mikrotik.py

A compliant device returns:

Desired identity : AnsibleMikrotik
Actual identity  : AnsibleMikrotik
DRIFT STATUS     : CLEAN

The validation script is read-only and does not modify the device configuration.

---

Python Remediation

When configuration drift is identified, the remediation script can restore the defined state:

python3 scripts/remediate_mikrotik.py

The device can then be validated again:

python3 scripts/validate_mikrotik.py

This provides a lightweight:

Detect → Remediate → Validate

workflow outside the main Ansible execution path.

---

Ansible and Python

The project deliberately uses both technologies for different purposes.

Ansible

Ansible provides the primary configuration-management layer for:

- Idempotent configuration
- Repeatable changes
- Network device management
- Compliance workflows
- Multi-device automation
- Future CI/CD integration

Python

Python provides a complementary scripting layer for:

- State validation
- Remediation
- Custom automation logic
- External integrations

This separation keeps configuration management in Ansible while retaining Python as a flexible automation layer.

---

MikroTik SSH Compatibility

The tested RouterOS environment required a specific SSH terminal compatibility configuration.

The inventory uses:

admin+cet512w

as the effective SSH username and:

ansible_network_cli_ssh_type=libssh

for the Ansible Network CLI connection.

These settings were required by the tested RouterOS environment and may not be necessary for every RouterOS deployment.

---

Security

Sensitive infrastructure information must not be committed to the repository.

Do not commit:

- Passwords
- Private keys
- API tokens
- Production inventories
- Configuration backups containing secrets
- ".env" files
- Vault passwords

The repository excludes local inventory files and generated network data through ".gitignore".

---

Design Principles

Reproducible

The project documents its dependencies and provides an example inventory so another engineer can reproduce the automation in their own environment.

Idempotent

The automation should only make configuration changes when the actual state differs from the desired state.

Validated

A configuration change is followed by explicit state validation rather than assuming that the configuration command succeeded.

Extensible

The current implementation provides a foundation for adding additional configuration and compliance policies.

Secure

Environment-specific configuration and credentials are kept outside the version-controlled project.

---

Roadmap

The current version establishes the core configuration-management and compliance workflow.

Future versions will expand the same architecture rather than replace it.

v1.1 — Extended Compliance

Planned controls include:

- Firewall compliance
- Management-service hardening
- NTP configuration
- DNS configuration
- Interface configuration
- Additional security policies
- Configuration drift reporting

v1.2 — Automation Quality

Potential additions include:

- "ansible-lint"
- Automated syntax validation
- CI/CD integration
- GitHub Actions
- Structured compliance reports

Future — Multi-Vendor Automation

If additional network platforms are introduced, the project can evolve toward multi-vendor automation, including Cisco and other network operating systems.

The goal is to move from device-specific configuration automation toward a reusable network configuration and compliance framework.

---

Project Status

Version: 1.0

Status: Implemented and validated

Environment: Real MikroTik RouterOS environment

Primary Automation: Ansible

Supporting Automation: Python

Management Protocol: SSH

Focus: Network Configuration Management, Compliance and Drift Remediation

---

License

No open-source license has been selected for the initial release.

A license can be added if the project is later intended for public reuse, redistribution, or community contribution.