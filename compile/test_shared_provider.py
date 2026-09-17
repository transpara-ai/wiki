#!/usr/bin/env python3
"""Tests for the reusable host-side provider boundary."""

import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent / "shared-provider"
sys.path.insert(0, str(HERE))
import provider_config  # noqa: E402


class ProviderConfigurationTests(unittest.TestCase):
    def document(self, host="unix:///run/civilization-docker.sock"):
        return {
            "docker_host": host,
            "observation_path": "/var/lib/civilization/provider-auth.json",
            "auth_policy_path": "/etc/civilization-provider/auth-policy.json",
        }

    def test_configuration_is_exact_and_unix_socket_only(self):
        self.assertEqual(provider_config.validate(self.document())["docker_host"],
                         "unix:///run/civilization-docker.sock")
        for document in (
            {**self.document(), "extra": "value"},
            self.document("tcp://127.0.0.1:2375"),
            self.document("unix://relative.sock"),
            {**self.document(), "observation_path": "relative.json"},
        ):
            with self.subTest(document=document), self.assertRaises(ValueError):
                provider_config.validate(document)

    def test_configuration_must_be_trusted_and_not_writable(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "config.json"
            with self.assertRaises(FileNotFoundError):
                provider_config.load(path, trusted_uid=os.getuid())
            path.write_text(__import__("json").dumps(self.document()))
            path.chmod(0o644)
            self.assertEqual(provider_config.load(path, trusted_uid=os.getuid()), self.document())
            path.chmod(0o664)
            with self.assertRaises(PermissionError):
                provider_config.load(path, trusted_uid=os.getuid())

    def test_wrapper_ignores_ambient_endpoint_and_uses_explicit_trusted_host(self):
        wrapper = runpy.run_path(str(HERE / "civilization-provider"))
        configuration = self.document()
        with patch.object(wrapper["provider_config"], "load", return_value=configuration), \
             patch.dict(os.environ, {"DOCKER_HOST": "tcp://attacker.invalid:2375"}), \
             patch.object(wrapper["os"], "geteuid", return_value=0), \
             patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as launch:
            self.assertEqual(wrapper["run"](["exec", "-i", "container", "codex"]), 0)
        command = launch.call_args.args[0]
        environment = launch.call_args.kwargs["env"]
        self.assertEqual(command[:4], ["/usr/bin/docker", "--host",
                                      "unix:///run/civilization-docker.sock", "exec"])
        self.assertNotIn("DOCKER_HOST", environment)

    def test_monitor_uses_same_explicit_endpoint(self):
        checker = runpy.run_path(str(HERE / "check-provider-auth.py"))
        configuration = self.document()
        with patch.dict(os.environ, {"DOCKER_HOST": "tcp://attacker.invalid:2375"}), \
             patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as launch:
            checker["docker_exec"](configuration, "codex", "login", "status")
        command = launch.call_args.args[0]
        self.assertEqual(command[:4], ["/usr/bin/docker", "--host",
                                      "unix:///run/civilization-docker.sock", "exec"])
        self.assertNotIn("DOCKER_HOST", launch.call_args.kwargs["env"])

    def test_image_build_keeps_release_version_after_cli_validation(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            argument_log = root / "docker-arguments"

            def executable(path, body):
                path.write_text("#!/bin/sh\nset -eu\n" + body)
                path.chmod(0o755)

            codex = root / "codex"
            claude = root / "claude"
            host = root / "codex-code-mode-host"
            executable(codex, "printf '%s\\n' 'codex-cli 0.153.4'\n")
            executable(claude, "printf '%s\\n' '2.1.263 (Claude Code)'\n")
            executable(host, "exit 0\n")
            executable(bin_dir / "git", "printf '%s\\n' '0123456789abcdef'\n")
            executable(bin_dir / "docker", "printf '%s\\n' \"$@\" > \"$DOCKER_ARGUMENT_LOG\"\n")

            environment = dict(os.environ)
            environment["PATH"] = str(bin_dir) + os.pathsep + environment["PATH"]
            environment["DOCKER_ARGUMENT_LOG"] = str(argument_log)
            subprocess.run([
                sys.executable, str(HERE / "build-image.py"),
                "--codex", str(codex), "--claude", str(claude),
                "--codex-code-mode-host", str(host),
            ], check=True, env=environment, capture_output=True, text=True)

            arguments = argument_log.read_text().splitlines()
            self.assertIn("transpara-provider:0.8.2", arguments)
            self.assertIn("org.opencontainers.image.version=0.8.2", arguments)
            self.assertIn("org.opencontainers.image.revision=0123456789abcdef", arguments)


if __name__ == "__main__":
    unittest.main()
