const { defineConfig } = require("@playwright/test");

const browserDist = process.env.KNOWLEDGE_HUB_BROWSER_DIST || "dist";
const browserPort = process.env.KNOWLEDGE_HUB_BROWSER_PORT || "8799";
const browserBase = `http://127.0.0.1:${browserPort}`;

module.exports = defineConfig({
  testDir: "./tests",
  testMatch: /.*\.spec\.js/,
  timeout: 30000,
  retries: 0,
  use: {
    browserName: "chromium",
    headless: true,
    baseURL: browserBase,
    trace: "retain-on-failure",
  },
  webServer: {
    command: `python3 -m http.server ${browserPort} --bind 127.0.0.1 --directory ${browserDist}`,
    url: `${browserBase}/index.html`,
    reuseExistingServer: false,
    timeout: 10000,
  },
});
