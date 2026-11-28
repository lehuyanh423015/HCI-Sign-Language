import { spawn } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:net';
import { tmpdir } from 'node:os';
import path from 'node:path';

const arg = (name, fallback) => {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
};
const url = arg('--url', 'http://127.0.0.1:5173/technical-sign-preview');
const reportPath = path.resolve(arg('--report', 'docs/reports/artifacts/TASK-0011B/browser-smoke.json'));
const screenshotPath = path.resolve(arg('--screenshot', 'docs/reports/artifacts/TASK-0011B/browser-smoke.png'));
const chromePath = arg('--chrome', 'C:/Program Files/Google/Chrome/Application/chrome.exe');
const expectedClip = arg('--clip', 'S001_MAIN');
const taskId = arg('--task', 'TASK-0011B');

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const freePort = await new Promise((resolve, reject) => {
  const server = createServer();
  server.once('error', reject);
  server.listen(0, '127.0.0.1', () => {
    const address = server.address();
    server.close(() => resolve(address.port));
  });
});

const profile = mkdtempSync(path.join(tmpdir(), `${taskId.toLowerCase()}-chrome-`));
const chrome = spawn(chromePath, [
  '--headless=new',
  '--no-first-run',
  '--no-default-browser-check',
  '--enable-unsafe-swiftshader',
  `--remote-debugging-port=${freePort}`,
  `--user-data-dir=${profile}`,
  '--window-size=1440,1000',
  url,
], { stdio: ['ignore', 'ignore', 'pipe'] });
let chromeStderr = '';
chrome.stderr.on('data', (chunk) => { chromeStderr += chunk.toString(); });

let target;
for (let attempt = 0; attempt < 100; attempt += 1) {
  try {
    const rows = await fetch(`http://127.0.0.1:${freePort}/json/list`).then((response) => response.json());
    target = rows.find((row) => row.type === 'page' && row.url.includes('/technical-sign-preview'));
    if (target) break;
  } catch {
    // Chrome DevTools endpoint is not ready yet.
  }
  await delay(100);
}
if (!target) {
  chrome.kill();
  throw new Error(`Chrome target did not start: ${chromeStderr.slice(-1000)}`);
}

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  ws.addEventListener('open', resolve, { once: true });
  ws.addEventListener('error', reject, { once: true });
});
let nextId = 1;
const pending = new Map();
const runtimeExceptions = [];
const consoleErrors = [];
const networkFailures = [];
ws.addEventListener('message', (event) => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) {
    const { resolve, reject } = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) reject(new Error(JSON.stringify(message.error)));
    else resolve(message.result);
  } else if (message.method === 'Runtime.exceptionThrown') {
    runtimeExceptions.push(message.params.exceptionDetails?.text ?? 'Runtime exception');
  } else if (message.method === 'Log.entryAdded' && message.params.entry?.level === 'error') {
    consoleErrors.push({
      text: message.params.entry.text,
      url: message.params.entry.url ?? null,
      source: message.params.entry.source ?? null,
    });
  } else if (message.method === 'Network.loadingFailed') {
    networkFailures.push({ url: message.params.requestId, error: message.params.errorText });
  }
});
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = nextId++;
  pending.set(id, { resolve, reject });
  ws.send(JSON.stringify({ id, method, params }));
});
const evaluate = async (expression) => {
  const result = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
  return result.result.value;
};

await Promise.all([
  send('Page.enable'),
  send('Runtime.enable'),
  send('Network.enable'),
  send('Log.enable'),
]);
await send('Page.reload', { ignoreCache: true });
for (let attempt = 0; attempt < 100; attempt += 1) {
  const ready = await evaluate(`(() => {
    const status = document.querySelector('[data-testid="viewer-status"]');
    return Boolean(status?.classList.contains('ready'));
  })()`);
  if (ready) break;
  await delay(100);
}
// The explicit reload can abort Chrome's initial navigation. Only runtime
// failures after the viewer is ready are relevant to this smoke check.
networkFailures.length = 0;

const snapshot = () => evaluate(`(() => ({
  title: document.title,
  status: document.querySelector('[data-testid="viewer-status"]')?.textContent?.trim() ?? null,
  statusClass: document.querySelector('[data-testid="viewer-status"]')?.className ?? null,
  clipList: document.querySelector('[data-testid="technical-clip-list"]')?.textContent?.trim() ?? null,
  time: Number.parseFloat(document.querySelector('[data-testid="animation-time"]')?.textContent ?? 'NaN'),
  camera: document.querySelector('[data-testid="technical-canvas"]')?.dataset.cameraPreset ?? null,
  canvasCount: document.querySelectorAll('[data-testid="technical-canvas"] canvas').length,
  buttons: [...document.querySelectorAll('.technical-controls button')].map((button) => ({ text: button.textContent?.trim(), disabled: button.disabled })),
}))()`);
const clickButton = (index) => evaluate(`(() => { const button = document.querySelectorAll('.technical-controls button')[${index}]; if (!button) return false; button.click(); return true; })()`);

const initial = await snapshot();
await delay(400);
const progressed = await snapshot();
await clickButton(0);
await delay(220);
const pausedStart = await snapshot();
await delay(450);
const pausedEnd = await snapshot();
await clickButton(0);
await delay(300);
const resumed = await snapshot();
await clickButton(1);
await delay(220);
const replayed = await snapshot();
await clickButton(2);
const loopToggled = await snapshot();
await clickButton(3);
const speedToggled = await snapshot();
await clickButton(5);
const handCamera = await snapshot();
await clickButton(4);
const resetCamera = await snapshot();
const relevantConsoleErrors = consoleErrors.filter((entry) => !entry.url?.endsWith('/favicon.ico'));

const screenshot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
mkdirSync(path.dirname(screenshotPath), { recursive: true });
writeFileSync(screenshotPath, Buffer.from(screenshot.data, 'base64'));

const checks = [
  ['page_route', initial.title.length > 0, { url, title: initial.title }],
  ['actual_glb_ready', initial.statusClass.includes('ready') && initial.status.includes(expectedClip), initial.status],
  ['expected_clip', initial.clipList === expectedClip, initial.clipList],
  ['webgl_canvas', initial.canvasCount === 1, initial.canvasCount],
  ['controls_enabled', initial.buttons.length === 6 && initial.buttons.every((button) => !button.disabled), initial.buttons],
  ['animation_progresses', progressed.time > initial.time, { initial: initial.time, progressed: progressed.time }],
  ['pause', Math.abs(pausedEnd.time - pausedStart.time) <= 0.03, { start: pausedStart.time, end: pausedEnd.time }],
  ['resume', resumed.time > pausedEnd.time, { paused: pausedEnd.time, resumed: resumed.time }],
  ['replay', replayed.time < 0.5, replayed.time],
  ['loop_toggle', loopToggled.buttons[2]?.text !== initial.buttons[2]?.text, loopToggled.buttons[2]?.text],
  ['speed_toggle', speedToggled.buttons[3]?.text !== initial.buttons[3]?.text, speedToggled.buttons[3]?.text],
  ['hand_camera', handCamera.camera === 'hand', handCamera.camera],
  ['camera_reset', resetCamera.camera === 'full', resetCamera.camera],
  ['no_runtime_exceptions', runtimeExceptions.length === 0, runtimeExceptions],
  ['no_console_errors', relevantConsoleErrors.length === 0, { relevant: relevantConsoleErrors, ignored_favicon: consoleErrors.filter((entry) => entry.url?.endsWith('/favicon.ico')) }],
  ['no_network_failures', networkFailures.length === 0, networkFailures],
].map(([id, passed, actual]) => ({ id, status: passed ? 'PASS' : 'FAIL', actual }));

const report = {
  schema_version: 1,
  artifact: `${taskId.toLowerCase()}_headless_browser_smoke`,
  status: checks.some((check) => check.status === 'FAIL') ? 'FAIL' : 'PASS',
  url,
  browser: chromePath,
  classification: 'LOCAL_TECHNICAL_STAGING_ONLY',
  expected_clip: expectedClip,
  checks,
  screenshot: screenshotPath,
};
mkdirSync(path.dirname(reportPath), { recursive: true });
writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
ws.close();
chrome.kill();
await Promise.race([
  new Promise((resolve) => chrome.once('exit', resolve)),
  delay(2000),
]);
try {
  rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
} catch (error) {
  console.warn(`WARN temporary Chrome profile cleanup deferred: ${error.message}`);
}
console.log(`${report.status} ${taskId} browser smoke (${checks.filter((check) => check.status === 'PASS').length}/${checks.length})`);
if (report.status !== 'PASS') process.exitCode = 1;
