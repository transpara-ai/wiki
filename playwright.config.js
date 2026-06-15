const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  testMatch: /.*\.spec\.js/,
  timeout: 30000,
  retries: 0,
  use: {
    browserName: "chromium",
    headless: true,
    baseURL: "http://127.0.0.1:8799",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "python3 -m http.server 8799 --bind 127.0.0.1 --directory dist",
    url: "http://127.0.0.1:8799/index.html",
    reuseExistingServer: false,
    timeout: 10000,
  },
});
