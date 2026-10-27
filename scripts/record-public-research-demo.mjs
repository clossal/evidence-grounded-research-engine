/*
 * State-aware recording controller for the public research demonstration.
 * Requires an externally installed `playwright` package and a local Chromium.
 * It records actual browser/API/Qwen activity; it never substitutes responses.
 */
import { createRequire } from "node:module";
import fs from "node:fs/promises";
import path from "node:path";

// NODE_PATH can point to an external recording-tools installation so the
// source-only application does not need to ship browser-automation packages.
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const baseUrl = process.env.DEMO_URL ?? "http://127.0.0.1:3006";
const chromiumPath = process.env.CHROMIUM_PATH ?? "/usr/bin/chromium";
const artifacts = path.resolve("artifacts");
const shots = path.join(artifacts, "screenshots");
const eventsPath = path.join(artifacts, "research-engine-demo-events.jsonl");
const rawDirectory = path.join(artifacts, "raw-video");
const rawName = "research-engine-demo.webm";

await fs.mkdir(shots, { recursive: true });
await fs.mkdir(rawDirectory, { recursive: true });
await fs.writeFile(eventsPath, "");

function stamp(event, details = {}) {
  return fs.appendFile(eventsPath, `${JSON.stringify({ timestamp: new Date().toISOString(), event, ...details })}\n`);
}

async function hold(page, milliseconds, reason) {
  await stamp("reading_hold_start", { milliseconds, reason });
  await page.waitForTimeout(milliseconds);
  await stamp("reading_hold_end", { reason });
}

async function gradualScroll(page, total = 680) {
  const steps = 6;
  for (let step = 0; step < steps; step += 1) {
    await page.mouse.wheel(0, total / steps);
    await page.waitForTimeout(400);
  }
  await stamp("scroll_complete", { pixels: total, steps });
}

async function selectOnly(page, labels) {
  const checks = [
    /International Scientific Report on the Safety/i,
    /phe-annual-report/i,
    /strategic-competition/i,
    /Artificial Intelligence Playbook/i,
    /world-development-report/i,
  ];
  for (const pattern of checks) {
    const checkbox = page.getByLabel(pattern);
    await checkbox.setChecked(labels.some((selected) => selected.test(pattern.source)));
  }
  await stamp("document_selection", { count: labels.length });
}

async function ask(page, { id, question, expectedCitation = null, expectAbstention = false, useMemory = false }) {
  const input = page.getByRole("textbox");
  const memory = page.getByLabel(/Use reviewed-memory/i);
  await memory.setChecked(useMemory);
  await input.fill(question);
  await stamp("question_entered", { id, question, useMemory });

  const apiResponse = page.waitForResponse((response) =>
    response.url().includes("/api/v1/public-research/ask") && response.request().method() === "POST",
    { timeout: 60000 },
  );
  const submit = page.getByRole("button", { name: /Ask with cited evidence/i });
  await submit.click();
  await stamp("question_submitted", { id });
  await page.getByRole("button", { name: /Researching/i }).waitFor({ state: "visible", timeout: 5000 }).catch(() => {});
  const response = await apiResponse;
  const payload = await response.json();
  await stamp("backend_response", {
    id,
    http_status: response.status(),
    run_id: payload.id ?? null,
    result_status: payload.status,
    evidence_count: payload.evidence?.length ?? 0,
    memory_used: payload.memory_used?.length ?? 0,
  });

  await page.getByRole("button", { name: /Ask with cited evidence/i }).waitFor({ state: "visible", timeout: 60000 });
  const rendered = expectAbstention
    ? page.getByText(/sufficient, clearly attributable evidence|cannot establish current or live facts/i)
    : page.getByRole("heading", { name: "Evidence used in this answer" });
  await rendered.waitFor({ state: "visible", timeout: 10000 });
  const visibleText = await page.locator("main").innerText();
  const displayedQuestion = await input.inputValue();
  if (displayedQuestion !== question || (expectAbstention ? payload.status !== "insufficient_evidence" : payload.status !== "answered")) {
    throw new Error(`Rendered state did not match the completed ${id} request.`);
  }
  if (expectedCitation && !visibleText.includes(expectedCitation)) {
    throw new Error(`Expected citation source was not rendered for ${id}.`);
  }
  await stamp("frontend_answer_rendered", { id, result_status: payload.status });
  await page.screenshot({ path: path.join(shots, `${id}-answer.png`) });
  await hold(page, expectAbstention ? 18000 : 20000, `${id}-answer`);
  return payload;
}

const browser = await chromium.launch({
  headless: true,
  executablePath: chromiumPath,
  args: ["--disable-notifications", "--no-first-run", "--disable-features=Translate"],
});
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  recordVideo: { dir: rawDirectory, size: { width: 1920, height: 1080 } },
  colorScheme: "dark",
});
const page = await context.newPage();
const consoleErrors = [];
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});
page.on("pageerror", (error) => consoleErrors.push(String(error)));

try {
  await stamp("recording_started", { baseUrl });
  await page.goto(baseUrl, { waitUntil: "networkidle", timeout: 30000 });
  await page.getByRole("heading", { name: "Research evidence workspace" }).waitFor({ state: "visible" });
  await stamp("library_rendered");
  await page.screenshot({ path: path.join(shots, "opening-library.png") });
  await hold(page, 15000, "opening-library");

  await selectOnly(page, [/Artificial Intelligence Playbook/i]);
  await ask(page, {
    id: "playbook-principles",
    question: "How many common principles does the UK AI Playbook define for government organisations?",
    expectedCitation: "Artificial Intelligence Playbook",
  });
  const firstDetails = page.locator("details summary").first();
  await firstDetails.scrollIntoViewIfNeeded();
  await firstDetails.click();
  const citation = page.getByRole("link", { name: /Open publisher PDF at page 9/i });
  await citation.scrollIntoViewIfNeeded();
  if (!(await citation.isVisible())) throw new Error("Citation link did not become visible.");
  await stamp("citation_opened", { question: "playbook-principles", href: await citation.getAttribute("href") });
  await page.screenshot({ path: path.join(shots, "playbook-citation.png") });
  await hold(page, 12000, "playbook-citation");

  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" }));
  await hold(page, 1200, "return-to-question");
  await selectOnly(page, [/International Scientific Report on the Safety/i]);
  await ask(page, {
    id: "safety-limitations",
    question: "What limitation does the interim AI safety report identify about current technical mitigation methods?",
    expectedCitation: "International Scientific Report",
  });
  await gradualScroll(page, 540);
  await hold(page, 10000, "safety-reading");

  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" }));
  await selectOnly(page, [/International Scientific Report on the Safety/i, /Artificial Intelligence Playbook/i]);
  await ask(page, {
    id: "cross-document",
    question: "Compare the AI safety report and UK AI Playbook on risk mitigation and accountability.",
    expectedCitation: "Evidence used in this answer",
    useMemory: true,
  });
  await gradualScroll(page, 420);
  await page.screenshot({ path: path.join(shots, "cross-document-answer.png") });
  await hold(page, 18000, "cross-document-reading");

  const ledger = page.getByRole("heading", { name: "3. Persistent reviewed-memory ledger" });
  await ledger.scrollIntoViewIfNeeded();
  await gradualScroll(page, 320);
  const reviewed = page.getByRole("button", { name: /evidence_supported/i });
  await reviewed.click();
  await page.getByRole("heading", { name: /Observation details/i }).waitFor({ state: "visible" });
  await stamp("memory_detail_opened");
  await page.screenshot({ path: path.join(shots, "memory-observation.png") });
  await hold(page, 18000, "memory-review");
  await page.getByRole("button", { name: "Close" }).click();

  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" }));
  await selectOnly(page, [/phe-annual-report/i]);
  await ask(page, {
    id: "out-of-corpus-abstention",
    question: "What was the exact 2026 inflation rate forecast in the selected 2019/20 PHE annual report?",
    expectAbstention: true,
  });
  await page.screenshot({ path: path.join(shots, "abstention.png") });
  await hold(page, 12000, "abstention-reading");
  await stamp("recording_complete", { console_errors: consoleErrors });
} catch (error) {
  await stamp("recording_failed", { error: String(error), console_errors: consoleErrors });
  throw error;
} finally {
  const video = page.video();
  await page.close();
  await context.close();
  await browser.close();
  if (video) {
    const finalRaw = path.join(rawDirectory, rawName);
    await fs.rename(await video.path(), finalRaw).catch(() => {});
  }
}
