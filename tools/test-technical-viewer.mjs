import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

function argument(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
}

const url = argument('--url', 'http://127.0.0.1:4173/technical-viewer');
const reportPath = path.resolve(argument('--report', 'docs/reports/artifacts/TASK-0003-browser-runtime.json'));
const screenshotPath = path.resolve(argument('--screenshot', 'docs/reports/artifacts/TASK-0003-browser-runtime.png'));
const fullScreenshotArgument = argument('--full-screenshot', '');
const fullScreenshotPath = fullScreenshotArgument ? path.resolve(fullScreenshotArgument) : null;
const chromeCandidates = [
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
];
const browserExecutable = chromeCandidates.find(existsSync);
if (!browserExecutable) throw new Error('Chrome/Edge executable not found');

const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
const profileDirectory = mkdtempSync(path.join(os.tmpdir(), 'hci-vsl-cdp-'));
const browser = spawn(browserExecutable, [
  '--headless=new',
  '--no-first-run',
  '--no-default-browser-check',
  '--disable-background-networking',
  '--remote-debugging-port=0',
  `--user-data-dir=${profileDirectory}`,
  '--window-size=1280,900',
  '--use-angle=swiftshader',
  '--enable-webgl',
  'about:blank',
], { stdio: 'ignore', windowsHide: true });

let closed = false;
browser.once('exit', () => { closed = true; });

async function waitForDebugPort() {
  const activePortFile = path.join(profileDirectory, 'DevToolsActivePort');
  for (let attempt = 0; attempt < 100; attempt += 1) {
    if (existsSync(activePortFile)) {
      const [port] = readFileSync(activePortFile, 'utf8').trim().split(/\r?\n/);
      return Number(port);
    }
    if (closed) throw new Error('Browser exited before exposing DevToolsActivePort');
    await delay(100);
  }
  throw new Error('Timed out waiting for Chrome DevTools port');
}

class CdpClient {
  constructor(webSocketUrl) {
    this.socket = new WebSocket(webSocketUrl);
    this.nextId = 1;
    this.pending = new Map();
    this.events = [];
    this.opened = new Promise((resolve, reject) => {
      this.socket.addEventListener('open', resolve, { once: true });
      this.socket.addEventListener('error', reject, { once: true });
    });
    this.socket.addEventListener('message', (event) => {
      const message = JSON.parse(event.data);
      if (message.id && this.pending.has(message.id)) {
        const { resolve, reject } = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) reject(new Error(message.error.message));
        else resolve(message.result);
      } else if (message.method) {
        this.events.push(message);
      }
    });
  }

  async send(method, params = {}) {
    await this.opened;
    const id = this.nextId;
    this.nextId += 1;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }

  close() {
    this.socket.close();
  }
}

async function evaluate(client, expression) {
  const result = await client.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text ?? 'Browser evaluation failed');
  return result.result.value;
}

async function waitFor(client, expression, description, timeoutMs = 30000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const value = await evaluate(client, expression);
    if (value) return value;
    await delay(150);
  }
  throw new Error(`Timed out waiting for ${description}`);
}

const report = {
  schema_version: 1,
  url,
  browser: browserExecutable,
  status: 'FAIL',
  checks: [],
};

try {
  const port = await waitForDebugPort();
  const endpoint = `http://127.0.0.1:${port}`;
  const targets = await (await fetch(`${endpoint}/json/list`)).json();
  const pageTarget = targets.find((target) => target.type === 'page');
  if (!pageTarget) throw new Error('No Chrome page target found');
  const client = new CdpClient(pageTarget.webSocketDebuggerUrl);
  await client.send('Runtime.enable');
  await client.send('Page.enable');
  await client.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'no-preference' }] });
  await client.send('Page.navigate', { url });
  await waitFor(client, "document.querySelector('[data-testid=viewer-status]')?.textContent?.startsWith('Sẵn sàng')", 'Three.js viewer readiness');

  const readiness = await evaluate(client, `(() => {
    const canvas = document.querySelector('[data-testid=technical-canvas] canvas');
    const status = document.querySelector('[data-testid=viewer-status]')?.textContent;
    return { status, canvas: Boolean(canvas), width: canvas?.width ?? 0, height: canvas?.height ?? 0 };
  })()`);
  report.checks.push({ id: 'gltf_and_canvas_ready', status: readiness.canvas && readiness.width > 0 ? 'PASS' : 'FAIL', evidence: readiness });
  if (fullScreenshotPath) {
    await evaluate(client, "[...document.querySelectorAll('button')].find(b => b.textContent === 'Phát lại').click()");
    await delay(20);
    await evaluate(client, "[...document.querySelectorAll('button')].find(b => b.textContent === 'Tạm dừng').click()");
    await delay(80);
    await evaluate(client, "window.scrollTo(0, document.querySelector('[data-testid=technical-canvas]').getBoundingClientRect().top + window.scrollY - 20)");
    await delay(120);
    const fullScreenshot = await client.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
    mkdirSync(path.dirname(fullScreenshotPath), { recursive: true });
    writeFileSync(fullScreenshotPath, Buffer.from(fullScreenshot.data, 'base64'));
    report.full_screenshot = fullScreenshotPath;
    await evaluate(client, 'window.scrollTo(0, 0)');
    await delay(80);
    await evaluate(client, "[...document.querySelectorAll('button')].find(b => b.textContent === 'Tiếp tục').click()");
    await delay(80);
  }

  const timeBefore = Number(await evaluate(client, "document.querySelector('[data-testid=animation-time]')?.textContent?.replace('s','')"));
  let timeAfter = timeBefore;
  for (let attempt = 0; attempt < 8 && timeAfter === timeBefore; attempt += 1) {
    await delay(150);
    timeAfter = Number(await evaluate(client, "document.querySelector('[data-testid=animation-time]')?.textContent?.replace('s','')"));
  }
  report.checks.push({ id: 'animation_progresses', status: timeAfter !== timeBefore ? 'PASS' : 'FAIL', evidence: { timeBefore, timeAfter } });

  await evaluate(client, "[...document.querySelectorAll('button')].find(b => b.textContent === 'Tạm dừng').click()")
  await delay(200);
  const pausedA = Number(await evaluate(client, "document.querySelector('[data-testid=animation-time]').textContent.replace('s','')"));
  await delay(350);
  const pausedB = Number(await evaluate(client, "document.querySelector('[data-testid=animation-time]').textContent.replace('s','')"));
  report.checks.push({ id: 'pause', status: Math.abs(pausedB - pausedA) <= 0.02 ? 'PASS' : 'FAIL', evidence: { pausedA, pausedB } });

  await evaluate(client, "[...document.querySelectorAll('button')].find(b => b.textContent === 'Tiếp tục').click()")
  await delay(300);
  const resumed = Number(await evaluate(client, "document.querySelector('[data-testid=animation-time]').textContent.replace('s','')"));
  report.checks.push({ id: 'resume', status: Math.abs(resumed - pausedB) > 0.05 ? 'PASS' : 'FAIL', evidence: { pausedB, resumed } });

  await evaluate(client, "[...document.querySelectorAll('button')].find(b => b.textContent === 'Phát lại').click()")
  await delay(180);
  const replayed = Number(await evaluate(client, "document.querySelector('[data-testid=animation-time]').textContent.replace('s','')"));
  report.checks.push({ id: 'replay', status: replayed <= 0.3 ? 'PASS' : 'FAIL', evidence: { replayed } });

  await evaluate(client, "[...document.querySelectorAll('button')].find(b => b.textContent.startsWith('Lặp lại:')).click()")
  await delay(80);
  const loopLabel = await evaluate(client, "[...document.querySelectorAll('button')].find(b => b.textContent.startsWith('Lặp lại:')).textContent")
  report.checks.push({ id: 'loop_toggle', status: loopLabel === 'Lặp lại: Tắt' ? 'PASS' : 'FAIL', evidence: { loopLabel } });

  await evaluate(client, "[...document.querySelectorAll('button')].find(b => b.textContent.startsWith('Tốc độ:')).click()")
  await delay(80);
  const speedLabel = await evaluate(client, "[...document.querySelectorAll('button')].find(b => b.textContent.startsWith('Tốc độ:')).textContent")
  report.checks.push({ id: 'speed_toggle', status: speedLabel === 'Tốc độ: 0,5×' ? 'PASS' : 'FAIL', evidence: { speedLabel } });

  const resetFound = await evaluate(client, "(() => { const b=[...document.querySelectorAll('button')].find(b => b.textContent==='Về góc ban đầu'); b?.click(); return Boolean(b); })()")
  await delay(100);
  const resetPreset = await evaluate(client, "document.querySelector('[data-testid=technical-canvas]').dataset.cameraPreset")
  const handFound = await evaluate(client, "(() => { const b=[...document.querySelectorAll('button')].find(b => b.textContent==='Cận cảnh tay phải'); b?.click(); return Boolean(b); })()")
  await delay(150);
  const handPreset = await evaluate(client, "document.querySelector('[data-testid=technical-canvas]').dataset.cameraPreset")
  report.checks.push({ id: 'camera_controls', status: resetFound && handFound && resetPreset === 'full' && handPreset === 'hand' ? 'PASS' : 'FAIL', evidence: { resetFound, resetPreset, handFound, handPreset } });

  const screenshot = await client.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  mkdirSync(path.dirname(screenshotPath), { recursive: true });
  writeFileSync(screenshotPath, Buffer.from(screenshot.data, 'base64'));
  report.screenshot = screenshotPath;
  report.runtime_exceptions = client.events.filter((event) => event.method === 'Runtime.exceptionThrown');
  report.status = report.checks.every((check) => check.status === 'PASS') && report.runtime_exceptions.length === 0 ? 'PASS' : 'FAIL';
  client.close();

  const version = await (await fetch(`${endpoint}/json/version`)).json();
  const browserClient = new CdpClient(version.webSocketDebuggerUrl);
  await browserClient.send('Browser.close');
  browserClient.close();
} finally {
  mkdirSync(path.dirname(reportPath), { recursive: true });
  writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  for (let attempt = 0; attempt < 30 && !closed; attempt += 1) await delay(100);
  if (!closed) browser.kill();
  try { rmSync(profileDirectory, { recursive: true, force: true }); } catch { /* Chrome may release files asynchronously. */ }
}

for (const check of report.checks) console.log(`${check.status} browser: ${check.id}`);
console.log(`${report.status} browser runtime: ${url}`);
if (report.status !== 'PASS') process.exitCode = 1;
