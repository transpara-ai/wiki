#!/usr/bin/env node
// Install Chromium portably. Playwright 1.56 has no Ubuntu 26.04 descriptor;
// its supported Ubuntu 24.04 browser bundle is compatible with this host.
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const env = { ...process.env };
if (process.platform === "linux" && !env.PLAYWRIGHT_HOST_PLATFORM_OVERRIDE) {
  let release = "";
  try { release = fs.readFileSync("/etc/os-release", "utf8"); } catch (_) { /* supported default */ }
  const id = (release.match(/^ID=(?:"([^"]+)"|([^\n]+))$/m) || []).slice(1).find(Boolean) || "";
  const version = (release.match(/^VERSION_ID=(?:"([^"]+)"|([^\n]+))$/m) || []).slice(1).find(Boolean) || "";
  if (id === "ubuntu" && Number.parseInt(version, 10) > 24) {
    env.PLAYWRIGHT_HOST_PLATFORM_OVERRIDE = "ubuntu24.04-x64";
    process.stdout.write(`Playwright: using supported ${env.PLAYWRIGHT_HOST_PLATFORM_OVERRIDE} browser bundle on Ubuntu ${version}.\n`);
  }
}

const executable = path.join(
  __dirname, "..", "node_modules", ".bin",
  process.platform === "win32" ? "playwright.cmd" : "playwright"
);
const result = spawnSync(executable, ["install", "chromium"], { env, stdio: "inherit" });
if (result.error) {
  process.stderr.write(`Playwright install failed to start: ${result.error.message}\n`);
  process.exit(1);
}
process.exit(result.status === null ? 1 : result.status);
