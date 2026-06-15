const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  testMatch: /.*\.spec\.js/,
  timeout: 30000,
  retries: 0,
  use: {
    browserName: "chromium",
    headless: true,
    baseURL: "http://127.0.0.1:8787",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "python3 -m http.server 8787 --bind 127.0.0.1 --directory dist",
    url: "http://127.0.0.1:8787/index.html",
    reuseExistingServer: true,
    timeout: 10000,
  },
});
