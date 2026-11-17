import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import os from 'node:os';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
let requiredFailures = 0;
let environmentFailures = 0;

function report(status, label, detail) {
  console.log(`${status.padEnd(14)} ${label}: ${detail}`);
}

function commandVersion(command, args = ['--version']) {
  const useCommandProcessor = process.platform === 'win32' && command.toLowerCase().endsWith('.cmd');
  const executable = useCommandProcessor ? (process.env.ComSpec ?? 'cmd.exe') : command;
  const executableArgs = useCommandProcessor ? ['/d', '/c', command, ...args] : args;
  const result = spawnSync(executable, executableArgs, { encoding: 'utf8', shell: false });
  return result.status === 0 ? `${result.stdout}${result.stderr}`.trim().split(/\r?\n/)[0] : null;
}

function discoverBlender() {
  const cliIndex = process.argv.indexOf('--blender');
  if (cliIndex >= 0 && process.argv[cliIndex + 1]) return path.resolve(process.argv[cliIndex + 1]);
  if (process.env.BLENDER_PATH) return process.env.BLENDER_PATH;
  const fromPath = spawnSync(process.platform === 'win32' ? 'where.exe' : 'which', ['blender'], { encoding: 'utf8' });
  if (fromPath.status === 0) return fromPath.stdout.trim().split(/\r?\n/)[0];
  if (process.platform === 'win32') {
    const base = path.join(process.env.ProgramFiles ?? 'C:\\Program Files', 'Blender Foundation');
    if (existsSync(base)) {
      for (const folder of readdirSync(base).sort().reverse()) {
        const candidate = path.join(base, folder, 'blender.exe');
        if (existsSync(candidate)) return candidate;
      }
    }
  }
  return null;
}

console.log('HCI Sign Language environment doctor');
report('PASS', 'Operating system', `${os.type()} ${os.release()} (${os.arch()})`);
const nodeMajor = Number(process.versions.node.split('.')[0]);
const nodeSupported = nodeMajor === 24 || nodeMajor === 26;
report(nodeSupported ? 'PASS' : 'FAIL', 'Node.js', `${process.version}; supported LTS majors: 24 or 26`);
if (!nodeSupported) requiredFailures += 1;

const npmCommand = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const npmVersion = commandVersion(npmCommand);
report(npmVersion ? 'PASS' : 'FAIL', 'npm', npmVersion ?? 'not found');
if (!npmVersion) requiredFailures += 1;
const gitVersion = commandVersion('git');
report(gitVersion ? 'PASS' : 'FAIL', 'Git', gitVersion ?? 'not found');
if (!gitVersion) requiredFailures += 1;

const requiredDirectories = ['apps/web', 'blender', 'data', 'schemas', 'tools', 'docs'];
for (const directory of requiredDirectories) {
  const present = existsSync(path.join(root, directory));
  report(present ? 'PASS' : 'FAIL', `Directory ${directory}`, present ? 'present' : 'missing');
  if (!present) requiredFailures += 1;
}

try {
  const rootPackage = JSON.parse(readFileSync(path.join(root, 'package.json'), 'utf8'));
  const webPackage = JSON.parse(readFileSync(path.join(root, 'apps/web/package.json'), 'utf8'));
  const validWorkspace = rootPackage.workspaces?.includes('apps/*') && webPackage.name === '@hci-sign/web';
  report(validWorkspace ? 'PASS' : 'FAIL', 'Project config', validWorkspace ? 'npm workspace is coherent' : 'workspace configuration is inconsistent');
  if (!validWorkspace) requiredFailures += 1;
} catch (error) {
  report('FAIL', 'Project config', error.message);
  requiredFailures += 1;
}

const installed = existsSync(path.join(root, 'node_modules'));
report(installed ? 'PASS' : 'FAIL', 'Dependencies', installed ? 'node_modules is present; use npm ci after pulling lockfile changes' : 'run npm ci');
if (!installed) requiredFailures += 1;

const blenderPath = discoverBlender();
if (!blenderPath || !existsSync(blenderPath)) {
  report('SKIPPED', 'Blender', 'not found; web development can continue. Set BLENDER_PATH for 3D checks.');
} else {
  const version = commandVersion(blenderPath);
  const compatible = version?.includes('4.5.16');
  report(compatible ? 'PASS' : 'FAIL', 'Blender', `${version ?? 'version unavailable'} at ${blenderPath}; project baseline is 4.5.16`);
  if (!compatible) environmentFailures += 1;
  report('NOT YET TESTED', 'MPFB', 'run the documented Blender preflight; doctor does not modify or open a .blend file');
}

report('NOT YET TESTED', '3D assets', 'run npm run validate:assets; browser playback requires a reviewed GLB');
console.log(`Doctor summary: ${requiredFailures} required failure(s), ${environmentFailures} 3D environment mismatch(es).`);
process.exitCode = requiredFailures + environmentFailures === 0 ? 0 : 1;
