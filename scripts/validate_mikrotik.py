import os
import subprocess
import sys

HOST = os.environ["MIKROTIK_HOST"]
PORT = os.environ.get("MIKROTIK_PORT", "2222")
USER = os.environ.get("MIKROTIK_USER", "admin")

DESIRED_STATE = {
    "identity": "AnsibleMikrotik"
}

result = subprocess.run(
    [
        "ssh",
        "-p",
        PORT,
        f"{USER}@{HOST}",
        "/system identity print",
    ],
    capture_output=True,
    text=True,
)

output = result.stdout
normalized = output.replace("\n", "").replace(" ", "")

actual_identity = None

if "name:" in normalized:
    actual_identity = normalized.split("name:", 1)[1].strip()

print(f"Desired identity : {DESIRED_STATE['identity']}")
print(f"Actual identity  : {actual_identity}")

if actual_identity == DESIRED_STATE["identity"]:
    print("DRIFT STATUS     : CLEAN")
    sys.exit(0)

print("DRIFT STATUS     : DETECTED")
sys.exit(2)
