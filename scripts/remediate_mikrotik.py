import os
import subprocess
import sys

HOST = os.environ["MIKROTIK_HOST"]
PORT = os.environ.get("MIKROTIK_PORT", "2222")
USER = os.environ.get("MIKROTIK_USER", "admin")

DESIRED_IDENTITY = "AnsibleMikrotik"

print(f"Remediating router identity to: {DESIRED_IDENTITY}")

result = subprocess.run(
    [
        "ssh",
        "-p",
        PORT,
        f"{USER}@{HOST}",
        f'/system identity set name="{DESIRED_IDENTITY}"',
    ],
    text=True,
)

if result.returncode != 0:
    print("REMEDIATION FAILED")
    sys.exit(1)

print("REMEDIATION COMPLETED")
