import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

function argument(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
}

const url = argument('--url', 'http://127.0.0.1:4173/technical-facial-viewer');
const reportPath = path.resolve(argument('--report', 'docs/reports/artifacts/TASK-0006/browser-runtime.json'));
const faceScreenshotPath = path.resolve(argument('--face-screenshot', 'docs/reports/artifacts/TASK-0006/browser-face.png'));
const fullScreenshotPath = path.resolve(argument('--full-screenshot', 'docs/reports/artifacts/TASK-0006/browser-full.png'));
const browserExecutable = [
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
].find(existsSync);
if (!browserExecutable) throw new Error('Chrome/Edge executable not found');

const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
const profileDirectory = mkdtempSync(path.join(os.tmpdir(), 'hci-vsl-facial-cdp-'));
const browser = spawn(browserExecutable, [
  '--headless=new', '--no-first-run', '--no-default-browser-check', '--disable-background-networking',
  '--remote-debugging-port=0', `--user-data-dir=${profileDirectory}`, '--window-size=1440,1000',
  '--use-angle=swiftshader', '--enable-webgl', 'about:blank',
], { stdio: 'ignore', windowsHide: true });
let closed = false;
browser.once('exit', () => { closed = true; });

async function waitForDebugPort() {
  const activePortFile = path.join(profileDirectory, 'DevToolsActivePort');
  for (let attempt = 0; attempt < 100; attempt += 1) {
    if (existsSync(activePortFile)) return Number(readFileSync(activePortFile, 'utf8').trim().split(/\r?\n/)[0]);
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
        const pending = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) pending.reject(new Error(message.error.message));
        else pending.resolve(message.result);
      } else if (message.method) this.events.push(message);
    });
  }
  async send(method, params = {}) {
    await this.opened;
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }
  close() { this.socket.close(); }
}

async function evaluate(client, expression) {
  const result = await client.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text ?? 'Browser evaluation failed');
  return result.result.value;
}

async function waitFor(client, expression, description, timeoutMs = 45000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const value = await evaluate(client, expression);
    if (value) return value;
    await delay(150);
  }
  throw new Error(`Timed out waiting for ${description}`);
}

async function clickByText(client, text) {
  return evaluate(client, `(() => { const button=[...document.querySelectorAll('button')].find((item)=>item.textContent==='${text}'); button?.click(); return Boolean(button); })()`);
}

async function capture(client, outputPath) {
  const screenshot = await client.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  mkdirSync(path.dirname(outputPath), { recursive: true });
  writeFileSync(outputPath, Buffer.from(screenshot.data, 'base64'));
}

const report = { schema_version: 1, url, browser: browserExecutable, status: 'FAIL', checks: [] };
try {
  const port = await waitForDebugPort();
  const endpoint = `http://127.0.0.1:${port}`;
  const targets = await (await fetch(`${endpoint}/json/list`)).json();
  const pageTarget = targets.find((target) => target.type === 'page');
  if (!pageTarget) throw new Error('No Chrome page target found');
  const client = new CdpClient(pageTarget.webSocketDebuggerUrl);
  await client.send('Runtime.enable');
  await client.send('Page.enable');
  await client.send('Page.navigate', { url });
  await waitFor(client, "document.querySelector('[data-testid=facial-viewer-status]')?.textContent?.startsWith('Sẵn sàng')", 'facial viewer readiness');

  const ready = await evaluate(client, `(() => {
    const canvas=document.querySelector('[data-testid=facial-canvas] canvas');
    return { canvas:Boolean(canvas), width:canvas?.width ?? 0, height:canvas?.height ?? 0,
      status:document.querySelector('[data-testid=facial-viewer-status]')?.textContent,
      morphs:document.querySelector('[data-testid=morph-target-list]')?.textContent,
      clips:document.querySelector('[data-testid=facial-clip-list]')?.textContent };
  })()`);
  const expectedTargets = ['NMM_BROW_RAISE_L','NMM_BROW_RAISE_R','NMM_EYE_BLINK_L','NMM_EYE_BLINK_R','NMM_LIPS_ROUND','NMM_LIPS_SPREAD'];
  const expectedClips = ['NMM_BLINK_TEST','NMM_BROW_TEST','NMM_MOUTH_TEST','TECH_HAND_FACE_TEST'];
  report.checks.push({ id: 'gltf_canvas_ready', status: ready.canvas && ready.width > 0 && ready.status.includes('master-avatar-v1-technical-demo.glb') ? 'PASS' : 'FAIL', evidence: ready });
  report.checks.push({ id: 'actual_morph_inventory', status: expectedTargets.every((name) => ready.morphs.includes(name)) ? 'PASS' : 'FAIL', evidence: ready.morphs });
  report.checks.push({ id: 'clip_inventory', status: expectedClips.every((name) => ready.clips.includes(name)) ? 'PASS' : 'FAIL', evidence: ready.clips });

  await clickByText(client, 'Tạm dừng');
  await delay(250);
  const pausedA = Number(await evaluate(client, "document.querySelector('[data-testid=facial-animation-time]').textContent.replace('s','')"));
  await delay(350);
  const pausedB = Number(await evaluate(client, "document.querySelector('[data-testid=facial-animation-time]').textContent.replace('s','')"));
  report.checks.push({ id: 'pause', status: Math.abs(pausedB - pausedA) <= 0.02 ? 'PASS' : 'FAIL', evidence: { pausedA, pausedB } });

  const morphValue = await evaluate(client, `(() => { const input=document.querySelector('[data-testid="morph-NMM_LIPS_ROUND"]'); input.value='0.75'; input.dispatchEvent(new Event('input',{bubbles:true})); input.dispatchEvent(new Event('change',{bubbles:true})); return input.value; })()`);
  await delay(120);
  report.checks.push({ id: 'morph_slider', status: morphValue === '0.75' ? 'PASS' : 'FAIL', evidence: { morphValue } });

  await clickByText(client, 'right');
  await delay(100);
  const gaze = await evaluate(client, "document.querySelector('[data-testid=facial-canvas]').dataset.gazePreset");
  report.checks.push({ id: 'gaze_control', status: gaze === 'right' ? 'PASS' : 'FAIL', evidence: { gaze } });

  await clickByText(client, 'Cận cảnh mặt');
  await delay(180);
  const facePreset = await evaluate(client, "document.querySelector('[data-testid=facial-canvas]').dataset.cameraPreset");
  await capture(client, faceScreenshotPath);
  await clickByText(client, 'Toàn thân');
  await delay(180);
  const fullPreset = await evaluate(client, "document.querySelector('[data-testid=facial-canvas]').dataset.cameraPreset");
  await capture(client, fullScreenshotPath);
  report.checks.push({ id: 'camera_presets', status: facePreset === 'face' && fullPreset === 'full' ? 'PASS' : 'FAIL', evidence: { facePreset, fullPreset } });

  await clickByText(client, 'Phát lại');
  await delay(300);
  const progressed = Number(await evaluate(client, "document.querySelector('[data-testid=facial-animation-time]').textContent.replace('s','')"));
  report.checks.push({ id: 'replay_and_progress', status: progressed > 0.05 ? 'PASS' : 'FAIL', evidence: { progressed } });
  await evaluate(client, "[...document.querySelectorAll('button')].find((item)=>item.textContent.startsWith('Loop:')).click()");
  await evaluate(client, "[...document.querySelectorAll('button')].find((item)=>item.textContent.startsWith('Tốc độ:')).click()");
  await delay(100);
  const toggles = await evaluate(client, `({ loop:[...document.querySelectorAll('button')].find((item)=>item.textContent.startsWith('Loop:')).textContent, speed:[...document.querySelectorAll('button')].find((item)=>item.textContent.startsWith('Tốc độ:')).textContent })`);
  report.checks.push({ id: 'loop_speed', status: toggles.loop === 'Loop: Tắt' && toggles.speed === 'Tốc độ: 0.5×' ? 'PASS' : 'FAIL', evidence: toggles });

  await clickByText(client, 'Đặt lại tất cả');
  await delay(180);
  const reset = await evaluate(client, `({
    morph:document.querySelector('[data-testid="morph-NMM_LIPS_ROUND"]').value,
    gaze:document.querySelector('[data-testid=facial-canvas]').dataset.gazePreset,
    camera:document.querySelector('[data-testid=facial-canvas]').dataset.cameraPreset,
    playback:document.querySelector('[data-testid=facial-playback-status]').textContent
  })`);
  report.checks.push({ id: 'reset_all', status: reset.morph === '0' && reset.gaze === 'center' && reset.camera === 'full' && reset.playback.startsWith('paused') ? 'PASS' : 'FAIL', evidence: reset });

  report.face_screenshot = faceScreenshotPath;
  report.full_screenshot = fullScreenshotPath;
  report.runtime_exceptions = client.events.filter((event) => event.method === 'Runtime.exceptionThrown');
  report.status = report.checks.every((item) => item.status === 'PASS') && report.runtime_exceptions.length === 0 ? 'PASS' : 'FAIL';
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
  try { rmSync(profileDirectory, { recursive: true, force: true }); } catch { /* browser file release can lag */ }
}

for (const item of report.checks) console.log(`${item.status} facial browser: ${item.id}`);
console.log(`${report.status} facial browser runtime: ${url}`);
if (report.status !== 'PASS') process.exitCode = 1;
