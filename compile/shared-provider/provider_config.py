"""Root-owned configuration for the shared provider host boundary."""

from __future__ import annotations

import json
import os
from pathlib import Path


CONFIG = Path("/etc/civilization-provider/config.json")
FIELDS = {"docker_host", "observation_path", "auth_policy_path"}


def validate(document: object) -> dict[str, str]:
    if not isinstance(document, dict) or set(document) != FIELDS:
        raise ValueError("provider configuration must contain exactly the supported fields")
    if not all(isinstance(value, str) and value for value in document.values()):
        raise ValueError("provider configuration values must be non-empty strings")
    docker_host = document["docker_host"]
    if not docker_host.startswith("unix://"):
        raise ValueError("provider Docker host must be an absolute Unix socket")
    socket = Path(docker_host.removeprefix("unix://"))
    if not socket.is_absolute() or ".." in socket.parts:
        raise ValueError("provider Docker host must be an absolute Unix socket")
    for key in ("observation_path", "auth_policy_path"):
        path = Path(document[key])
        if not path.is_absolute() or ".." in path.parts:
            raise ValueError(f"{key} must be an absolute path")
    return dict(document)


def load(path: Path = CONFIG, trusted_uid: int = 0) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError("root-owned provider configuration is not installed")
    stat = path.stat()
    if stat.st_uid != trusted_uid or stat.st_mode & 0o022:
        raise PermissionError("provider configuration must be owned by root and not group/world writable")
    return validate(json.loads(path.read_text()))


def write(path: Path, document: object) -> None:
    """Atomically write configuration; caller must already be root."""
    if os.geteuid() != 0:
        raise PermissionError("provider configuration installation requires root")
    validated = validate(document)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(validated, indent=2, sort_keys=True) + "\n")
    os.chmod(temporary, 0o644)
    os.chown(temporary, 0, 0)
    temporary.replace(path)
