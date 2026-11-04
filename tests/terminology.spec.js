const {test, expect} = require("@playwright/test");
const fs = require("node:fs/promises");
const {observation, snapshot} = require("./fixtures/terminology");

test("candidate review exports a digest-bound draft without any server mutation", async ({page}) => {
  const calls = [];
  await page.route("**/api/terminology/**", route => {
    calls.push(route.request().method());
    return route.fulfill({json:snapshot()});
  });
  await page.goto("/terminology.html");
  await page.getByRole("button", {name:"flux adapter", exact:false}).click();
  await expect(page.getByText("ASD vocabulary is unavailable. This phrase is unassessed, not a confirmed violation.")).toBeVisible();
  await expect(page.locator(".term-evidence")).toContainText("<script>");
  expect(await page.evaluate(() => window.pwned)).toBeUndefined();
  await page.getByLabel("Classification", {exact:true}).selectOption("immutable");
  await page.getByLabel("Definition and meaning boundaries").fill("An example product component.");
  await page.screenshot({path:test.info().outputPath("terminology-desktop.png"),fullPage:true});
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", {name:"Download draft proposal"}).click();
  const download = await downloadPromise;
  const proposal = JSON.parse(await fs.readFile(await download.path(), "utf8"));
  expect(proposal).toMatchObject({schema_version:1,state:"draft",candidate_id:"candidate-one",
    decision:"immutable",expected_dictionary_digest:"a".repeat(64),term:"flux adapter",
    term_class:"technical_noun",approved_forms:["flux adapter"],context_digests:["b".repeat(64)]});
  expect(proposal.approved_by).toBeUndefined();
  await expect(page.getByRole("status")).toContainText("remains pending");
  expect(calls).toEqual(["GET"]);
});

test("regular English remains a proposal, empty collections and narrow layout are usable", async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.route("**/api/terminology/**", route => route.fulfill({json:snapshot()}));
  await page.goto("/terminology.html");
  await page.getByRole("button", {name:"flux adapter",exact:false}).click();
  await page.getByLabel("Classification", {exact:true}).selectOption("regular_english");
  await expect(page.getByText("Propose regular English. This does not add a writing-rule exemption.")).toBeVisible();
  await expect(page.getByLabel("Definition and meaning boundaries")).toBeHidden();
  await page.screenshot({path:test.info().outputPath("terminology-mobile.png"),fullPage:true});
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", {name:"Download draft proposal"}).click();
  const download = await downloadPromise;
  const proposal = JSON.parse(await fs.readFile(await download.path(), "utf8"));
  expect(proposal.decision).toBe("regular_english");
  expect(proposal.approved_forms).toEqual([]);
  await page.getByRole("button", {name:"Transpara Dictionary",exact:true}).click();
  await expect(page.getByText("The Human-owned dictionary has no approved terms yet.")).toBeVisible();
  await page.getByRole("button", {name:"Source revision",exact:true}).click();
  await expect(page.getByText("Dictionary version 0.1.0",{exact:true})).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.keyboard.press("Tab");
  expect(await page.evaluate(() => document.activeElement.tagName)).not.toBe("BODY");
});

test("refresh failure invalidates the selected draft and reports unavailable state", async ({page}) => {
  let available = true;
  await page.route("**/api/terminology/**", route => available
    ? route.fulfill({json:snapshot()})
    : route.fulfill({status:503,json:{error:"No terminology snapshot is configured."}}));
  await page.goto("/terminology.html");
  await page.getByRole("button", {name:"flux adapter",exact:false}).click();
  await page.getByLabel("Classification", {exact:true}).selectOption("regular_english");
  await expect(page.getByRole("button", {name:"Download draft proposal"})).toBeEnabled();
  available = false;
  await page.getByRole("button", {name:"Refresh",exact:true}).click();
  await expect(page.getByRole("status")).toContainText("No terminology snapshot");
  await expect(page.locator("#term-detail")).toBeHidden();
  await expect(page.locator("#term-download")).toBeDisabled();
  await expect(page.getByText("No current snapshot. ASD conformance is not assessed.")).toBeVisible();
});

test("legacy snapshots with complete line hashes remain visible but cannot export a decision", async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  const data = snapshot();
  for (const key of ["context_binding", "term", "start", "end"])
    delete data.candidates[0].observations[0][key];
  await page.route("**/api/terminology/**", route => route.fulfill({json:data}));
  await page.goto("/terminology.html");
  await page.getByRole("button", {name:"flux adapter",exact:false}).click();
  await page.getByLabel("Classification", {exact:true}).selectOption("regular_english");
  await expect(page.getByText("The shown evidence needs current occurrence bindings and valid source spans.",{exact:false})).toBeVisible();
  await expect(page.locator(".term-evidence")).toContainText("Use the flux adapter.");
  await expect(page.getByRole("button", {name:"Download draft proposal"})).toBeDisabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({path:test.info().outputPath("terminology-legacy-mobile.png"),fullPage:true});
});

test("current occurrence snapshots export the exact displayed hashes", async ({page}) => {
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  page.on("console", message => {if (message.type() === "error") errors.push(message.text());});
  // The optional path exercises an actual fresh core export during integration.
  // CI uses a current-format Unicode fixture without an external dependency.
  const data = process.env.WIKI_TERMINOLOGY_TEST_SNAPSHOT
    ? JSON.parse(await fs.readFile(process.env.WIKI_TERMINOLOGY_TEST_SNAPSHOT, "utf8")) : snapshot();
  if (!process.env.WIKI_TERMINOLOGY_TEST_SNAPSHOT)
    Object.assign(data.candidates[0].observations[0], {sentence:"🙂 Use the flux adapter.", start:10, end:22});
  const index = Math.max(0, data.candidates.slice(0,100).findIndex(candidate => candidate.observations.length > 1));
  const candidate = data.candidates[index];
  await page.route("**/api/terminology/**", route => route.fulfill({json:data}));
  await page.goto("/terminology.html");
  await page.locator(".term-candidate").nth(index).click();
  await expect(page.locator(".term-evidence")).toHaveCount(Math.min(10,candidate.observations.length));
  await page.getByLabel("Classification", {exact:true}).selectOption("regular_english");
  await expect(page.getByRole("button", {name:"Download draft proposal"})).toBeEnabled();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", {name:"Download draft proposal"}).click();
  const proposal = JSON.parse(await fs.readFile(await (await downloadPromise).path(), "utf8"));
  expect(proposal.context_digests).toEqual(candidate.observations.slice(0,10).map(item => item.context_digest));
  expect(proposal.term).toBe(candidate.term);
  expect(errors).toEqual([]);
  await page.screenshot({path:test.info().outputPath("terminology-occurrence-desktop.png"),fullPage:true});
});

test("malformed current source spans cannot export a decision", async ({page}) => {
  const data = snapshot();
  data.candidates[0].observations[0].end = 1000;
  await page.route("**/api/terminology/**", route => route.fulfill({json:data}));
  await page.goto("/terminology.html");
  await page.getByRole("button", {name:"flux adapter",exact:false}).click();
  await page.getByLabel("Classification", {exact:true}).selectOption("regular_english");
  await expect(page.getByRole("button", {name:"Download draft proposal"})).toBeDisabled();
});

test("large candidates export only the displayed evidence and require hashes for that evidence", async ({page}) => {
  const data = snapshot();
  data.candidates[0].observations = Array.from({length:11}, (_, index) => ({
    ...observation("Context " + index + " flux adapter"), line:index + 1,
    context_digest:index < 10 ? String(index).repeat(64) : undefined}));
  await page.route("**/api/terminology/**", route => route.fulfill({json:data}));
  await page.goto("/terminology.html");
  await page.getByRole("button", {name:"flux adapter",exact:false}).click();
  await expect(page.getByText("Showing 10 of 11 observations.",{exact:false})).toBeVisible();
  await expect(page.locator(".term-evidence")).toHaveCount(10);
  await expect(page.getByText("Context 10 flux adapter",{exact:true})).toHaveCount(0);
  await page.getByLabel("Classification", {exact:true}).selectOption("regular_english");
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", {name:"Download draft proposal"}).click();
  const download = await downloadPromise;
  const proposal = JSON.parse(await fs.readFile(await download.path(), "utf8"));
  expect(proposal.context_digests).toEqual(Array.from({length:10}, (_, index) => String(index).repeat(64)));
  delete data.candidates[0].observations[0].context_digest;
  await page.getByRole("button", {name:"Refresh",exact:true}).click();
  await page.getByRole("button", {name:"flux adapter",exact:false}).click();
  await page.getByLabel("Classification", {exact:true}).selectOption("regular_english");
  await expect(page.getByRole("button", {name:"Download draft proposal"})).toBeDisabled();
});
