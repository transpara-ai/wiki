#!/usr/bin/env python3
"""Record non-secret health for the deployed Codex and Claude identities."""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys

LOCAL_LIBRARY = Path(__file__).resolve().parent
INSTALLED_LIBRARY = Path("/usr/local/lib/civilization-provider")
sys.path.insert(0, str(LOCAL_LIBRARY if (LOCAL_LIBRARY / "provider_config.py").is_file()
                       else INSTALLED_LIBRARY))
import provider_config  # noqa: E402

CONTAINER = "transpara-shared-provider"


def docker_exec(configuration: dict[str, str], *command: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("DOCKER_HOST", None)
    return subprocess.run(
        ["/usr/bin/docker", "--host", configuration["docker_host"],
         "exec", CONTAINER, *command],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )


def codex_status(configuration: dict[str, str], policy: dict[str, object]) -> dict[str, object]:
    result = docker_exec(configuration, "codex", "login", "status")
    message = (result.stdout or result.stderr).strip()
    logged_in = result.returncode == 0 and "Logged in using" in message
    method = "chatgpt-subscription" if "ChatGPT" in message else "unknown"
    policy = policy.get("codex", {})
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


def claude_status(configuration: dict[str, str], policy: dict[str, object]) -> dict[str, object]:
    result = docker_exec(
        configuration,
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
        configuration,
        "python3",
        "-c",
        "from pathlib import Path; "
        "e=dict(x.split(b'=',1) for x in Path('/proc/1/environ').read_bytes().split(b'\\0') if b'=' in x); "
        "s=Path('/run/secrets/claude_oauth_token').read_text().strip().encode(); "
        "print('yes' if e.get(b'CLAUDE_CODE_OAUTH_TOKEN') == s and bool(s) else 'no')",
    )
    token_loaded = token_check.returncode == 0 and token_check.stdout.strip() == "yes"
    policy = policy.get("claude", {})
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
    configuration = provider_config.load()
    policy = json.loads(Path(configuration["auth_policy_path"]).read_text())
    providers = {
        "codex": codex_status(configuration, policy),
        "claude": claude_status(configuration, policy),
    }
    document = {
        "checked_at": dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z"),
        "healthy": all(bool(item["healthy"]) for item in providers.values()),
        "providers": providers,
    }
    output = Path(configuration["observation_path"])
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    os.chmod(temporary, 0o600)
    temporary.replace(output)
    print(json.dumps(document, sort_keys=True))
    return 0 if document["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
