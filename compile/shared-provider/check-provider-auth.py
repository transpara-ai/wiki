#!/usr/bin/env python3
"""Record non-secret health for the deployed Codex and Claude identities."""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys


CONTAINER = "transpara-shared-provider"
OUTPUT = Path('/Transpara/transpara-ai/deployments/shared-provider-velia/state/provider-auth.json')
AUTH_POLICY = Path('/Transpara/transpara-ai/deployments/shared-provider-velia/config/provider-auth-policy.json')


def docker_exec(*command: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("DOCKER_HOST", "unix:///var/run/docker.sock")
    return subprocess.run(
        ["/usr/bin/docker", "exec", CONTAINER, *command],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )


def codex_status() -> dict[str, object]:
    result = docker_exec("codex", "login", "status")
    message = (result.stdout or result.stderr).strip()
    logged_in = result.returncode == 0 and "Logged in using" in message
    method = "chatgpt-subscription" if "ChatGPT" in message else "unknown"
    policy = json.loads(AUTH_POLICY.read_text()).get("codex", {})
    status_line = next(
        (line.strip() for line in message.splitlines() if "Logged in using" in line),
        "login unavailable",
    )
    return {
        "healthy": logged_in and method == "chatgpt-subscription",
        "auth_method": method,
        "account": policy.get("account", ""),
        "display_name": policy.get("display_name", ""),
        "detail": status_line,
    }


def claude_status() -> dict[str, object]:
    result = docker_exec(
        "sh",
        "-ec",
        'export CLAUDE_CODE_OAUTH_TOKEN="$(cat /run/secrets/claude_oauth_token)"; '
        "exec claude auth status",
    )
    raw = (result.stdout or result.stderr).strip()
    start = raw.find("{")
    try:
        status = json.loads(raw[start:]) if start >= 0 else {}
    except json.JSONDecodeError:
        status = {}
    token_check = docker_exec(
        "python3",
        "-c",
        "from pathlib import Path; "
        "e=dict(x.split(b'=',1) for x in Path('/proc/1/environ').read_bytes().split(b'\\0') if b'=' in x); "
        "s=Path('/run/secrets/claude_oauth_token').read_text().strip().encode(); "
        "print('yes' if e.get(b'CLAUDE_CODE_OAUTH_TOKEN') == s and bool(s) else 'no')",
    )
    token_loaded = token_check.returncode == 0 and token_check.stdout.strip() == "yes"
    policy = json.loads(AUTH_POLICY.read_text()).get("claude", {})
    logged_in = result.returncode == 0 and status.get("loggedIn") is True and token_loaded
    return {
        "healthy": logged_in,
        "auth_method": status.get("authMethod", "unknown"),
        "credential_mode": policy.get("auth_mode", "unknown"),
        "expected_expires_at": policy.get("expected_expires_at", ""),
        "long_lived_token_loaded": token_loaded,
        "account": status.get("email") or policy.get("account", ""),
        "display_name": policy.get("display_name", ""),
        "organization": status.get("orgName") or policy.get("organization", ""),
        "subscription_type": status.get("subscriptionType") or policy.get("subscription_type", ""),
    }


def main() -> int:
    providers = {"codex": codex_status(), "claude": claude_status()}
    document = {
        "checked_at": dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z"),
        "healthy": all(bool(item["healthy"]) for item in providers.values()),
        "providers": providers,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    os.chmod(temporary, 0o600)
    os.chown(temporary, 1000, 1000)
    temporary.replace(OUTPUT)
    print(json.dumps(document, sort_keys=True))
    return 0 if document["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
