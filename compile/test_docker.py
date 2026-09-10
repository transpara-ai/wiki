#!/usr/bin/env python3
"""Opt-in Docker integration test using an isolated, disposable wiki checkout."""
import hashlib
import http.client
import json
import os
import pathlib
import secrets
import shlex
import shutil
import socket
import subprocess
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCKER = shlex.split(os.environ.get("WIKI_TEST_DOCKER_COMMAND", "docker"))


def main():
    with tempfile.TemporaryDirectory(prefix="wiki-docker-test-") as scratch:
        repos = pathlib.Path(scratch)
        wiki = repos / "wiki"
        shutil.copytree(ROOT, wiki, ignore=shutil.ignore_patterns(
            ".git", ".venv", "node_modules", "__pycache__", ".env", ".env.*",
            "dist", "dist-*", ".cache", "test-results", "playwright-report",
            "*-authorization.json", ".wiki-write.lock"))
        sibling = repos / "docker-source-fixture"
        sibling.mkdir()
        (sibling / "README.md").write_text("# Docker source fixture\n\nRead-only source repository.\n")
        subprocess.run(["git", "init", "--quiet", str(sibling)], check=True)
        subprocess.run(["git", "-C", str(sibling), "remote", "add", "origin",
                        "https://github.com/transpara-ai/docker-source-fixture.git"], check=True)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        token = secrets.token_hex(32)
        env = dict(os.environ, WIKI_UID=str(os.getuid()), WIKI_GID=str(os.getgid()),
                   WIKI_REPOS_DIR=str(repos), WIKI_PORT=str(port),
                   KNOWLEDGE_HUB_AUTHORING_TOKEN=token,
                   KNOWLEDGE_HUB_ALLOWED_HOSTS="wiki-test.example.ts.net,wiki-test.example.ts.net:443",
                   KNOWLEDGE_HUB_REFRESH_SECONDS="2")
        compose = DOCKER + ["compose", "--project-name", "wiki-test-" + secrets.token_hex(4),
                   "--project-directory", str(wiki), "-f", str(wiki / "compose.yaml")]

        def run(*args, timeout=240):
            result = subprocess.run(compose + list(args), env=env, text=True,
                                    capture_output=True, timeout=timeout)
            if result.returncode:
                raise AssertionError(result.stderr or result.stdout)
            return result.stdout.strip()

        def request(method, path, body=None, authorized=False):
            headers = {"Host": "wiki-test.example.ts.net"}
            if authorized:
                headers["X-CivWiki-Authoring-Token"] = token
            if body is not None:
                headers["Content-Type"] = "multipart/form-data; boundary=wiki-docker-test"
            client = http.client.HTTPConnection("127.0.0.1", port, timeout=240)
            try:
                client.request(method, path, body=body, headers=headers)
                response = client.getresponse()
                data = response.read()
                return response.status, data
            finally:
                client.close()

        try:
            run("config", "--quiet")
            run("up", "-d", "--no-build", "--wait", "--wait-timeout", "180")
            assert request("GET", "/api/health")[0] == 200
            version = json.loads((wiki / "package.json").read_text())["version"]
            assert json.loads(request("GET", "/version.json")[1]) == {"version": version}
            assert request("POST", "/api/rebuild")[0] == 401, "writes require the editor token"
            container = run("ps", "-q", "wiki")
            info = json.loads(subprocess.check_output(DOCKER + ["inspect", container]))[0]
            assert info["HostConfig"]["PortBindings"]["8787/tcp"][0]["HostIp"] == "127.0.0.1"
            assert info["HostConfig"]["ReadonlyRootfs"] is True
            assert run("exec", "-T", "wiki", "id", "-u") == str(os.getuid())
            run("exec", "-T", "wiki", "python3", "-c",
                "from pathlib import Path\n"
                "try: Path('/Transpara/transpara-ai/repos/docker-source-fixture/blocked').write_text('x')\n"
                "except OSError: pass\n"
                "else: raise AssertionError('sibling repositories must be read-only')")
            assert request("GET", "/repo-docker-source-fixture.html")[0] == 200

            fields = {"target_slug": "competitor-cognite-data-fusion", "space": "competition",
                      "section": "competitors", "steward": "transpara"}
            content = "Container persistence test — café.\n  Original whitespace.\n"
            parts = [f'--wiki-docker-test\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'
                     for key, value in fields.items()]
            parts.append('--wiki-docker-test\r\nContent-Disposition: form-data; name="documents"; '
                         'filename="container-test.txt"\r\nContent-Type: text/plain\r\n\r\n'
                         + content + '\r\n--wiki-docker-test--\r\n')
            status, data = request("POST", "/api/ingest", "".join(parts).encode(), authorized=True)
            result = json.loads(data)
            assert status == 200 and result["refresh"]["ok"], result
            source = wiki / result["saved"][0]["path"]
            assert source.read_text() == content
            article = wiki / "wiki/competitor-cognite-data-fusion.md"
            assert "stale_since:" in article.read_text()
            source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            article_hash = hashlib.sha256(article.read_bytes()).hexdigest()

            discovery = json.loads(request("GET", "/api/spaces")[1])
            assert any(s["key"] == "devops" and s["can_create_article"] for s in discovery["spaces"])
            devops_fields = {"new_article": "true", "name": "Container corpus fixture",
                             "space": "devops", "section": "containers", "steward": "transpara",
                             "article_markdown": "# Container corpus fixture\n\nVerified procedure from the imported corpus.\n"}
            devops_parts = [f'--wiki-docker-test\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'
                            for key, value in devops_fields.items()]
            devops_parts.append('--wiki-docker-test\r\nContent-Disposition: form-data; name="documents"; '
                                'filename="devops-source.txt"\r\nContent-Type: text/plain\r\n\r\n'
                                + content + '\r\n--wiki-docker-test--\r\n')
            devops_body = "".join(devops_parts).encode()
            status, data = request("POST", "/api/ingest", devops_body, authorized=True)
            devops_result = json.loads(data)
            assert status == 200 and devops_result["refresh"]["ok"], devops_result
            assert devops_result["article_content_written"]
            devops_href = "/" + devops_result["article_href"]
            devops_page = request("GET", devops_href)[1]
            assert b"Verified procedure from the imported corpus." in devops_page
            assert b"summary re-derivation pending" not in devops_page
            assert b"Container corpus fixture" in request("GET", "/devops/index.html")[1]
            devops_source = wiki / devops_result["saved"][0]["path"]
            assert devops_source.read_text() == content
            assert request("GET", "/" + devops_result["source_hrefs"][0]["href"])[0] == 200
            assert request("POST", "/api/ingest", devops_body, authorized=True)[0] == 422
            devops_article = wiki / "wiki" / (devops_result["created_article"]["slug"] + ".md")
            devops_article_bytes = devops_article.read_bytes()
            assert b"classification: internal" in devops_article_bytes
            ledger = (wiki / "compile/ingest-ledger.jsonl").read_bytes()
            manifest = {p.name: p.read_bytes() for p in (wiki / "raw/inbox/manifest.d").glob("*.jsonl")}
            assert request("GET", "/" + result["source_hrefs"][0]["href"])[0] == 200

            deadline = time.monotonic() + 45
            while "refresh:" not in run("logs", "--no-color", "refresh"):
                if time.monotonic() > deadline:
                    raise AssertionError("refresh sidecar did not run")
                time.sleep(1)

            run("up", "-d", "--no-build", "--force-recreate", "--wait", "--wait-timeout", "180")
            assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
            assert hashlib.sha256(article.read_bytes()).hexdigest() == article_hash
            assert devops_article.read_bytes() == devops_article_bytes
            assert devops_source.read_text() == content
            assert b"Verified procedure from the imported corpus." in request("GET", devops_href)[1]
            assert (wiki / "compile/ingest-ledger.jsonl").read_bytes() == ledger
            assert {p.name: p.read_bytes() for p in (wiki / "raw/inbox/manifest.d").glob("*.jsonl")} == manifest
            assert request("GET", "/" + result["source_hrefs"][0]["href"])[0] == 200
            assert b"$175,000" in request("GET", "/competitor-cognite-data-fusion.html")[1]
            print("ok Docker: private port, token-protected writes, read-only siblings, source ingestion, DevOps article creation and rendered prose, periodic refresh, recreation persistence, version " + version)
        finally:
            run("down", "--timeout", "10", timeout=60)


if __name__ == "__main__":
    main()
