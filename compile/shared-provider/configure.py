#!/usr/bin/env python3
"""Install the reusable, root-owned Civilization provider host boundary."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil

import provider_config


HERE = Path(__file__).resolve().parent
LIBRARY = Path("/usr/local/lib/civilization-provider")
WRAPPER = Path("/usr/local/bin/civilization-provider")
CHECKER = Path("/usr/local/libexec/civilization-check-provider-auth")


def install(source: Path, destination: Path, mode: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    shutil.copyfile(source, temporary)
    os.chmod(temporary, mode)
    os.chown(temporary, 0, 0)
    temporary.replace(destination)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker-host", required=True)
    parser.add_argument("--observation", type=Path, required=True)
    parser.add_argument("--auth-policy", type=Path, required=True)
    args = parser.parse_args(argv)
    if os.geteuid() != 0:
        raise PermissionError("provider boundary installation requires root")
    document = provider_config.validate({
        "docker_host": args.docker_host,
        "observation_path": str(args.observation),
        "auth_policy_path": str(args.auth_policy),
    })
    provider_config.write(provider_config.CONFIG, document)
    install(HERE / "provider_config.py", LIBRARY / "provider_config.py", 0o644)
    install(HERE / "check-provider-auth.py", CHECKER, 0o755)
    # Install the public entrypoint last. Until this replace, the prior wrapper
    # remains intact; afterward all of its configuration dependencies exist.
    install(HERE / "civilization-provider", WRAPPER, 0o755)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
