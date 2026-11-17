import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import os from 'node:os';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
let requiredFailures = 0;
let environmentFailures = 0;

function readLocalBlenderConfig() {
  const envFile = path.join(root, '.env.local');
  if (!existsSync(envFile)) return {};
  const values = {};
  for (const rawLine of readFileSync(envFile, 'utf8').split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) continue;
    const separator = line.indexOf('=');
    if (separator < 1) continue;
    const key = line.slice(0, separator).trim();
    let value = line.slice(separator + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (key === 'BLENDER_EXECUTABLE' || key === 'BLENDER_PATH') values[key] = value;
  }
  return values;
}

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
  if (cliIndex >= 0 && process.argv[cliIndex + 1]) return { executable: path.resolve(process.argv[cliIndex + 1]), source: '--blender' };
  if (process.env.BLENDER_EXECUTABLE) return { executable: process.env.BLENDER_EXECUTABLE, source: 'BLENDER_EXECUTABLE' };
  const localConfig = readLocalBlenderConfig();
  if (localConfig.BLENDER_EXECUTABLE) return { executable: localConfig.BLENDER_EXECUTABLE, source: '.env.local:BLENDER_EXECUTABLE' };
  if (process.env.BLENDER_PATH) return { executable: process.env.BLENDER_PATH, source: 'BLENDER_PATH (legacy)' };
  if (localConfig.BLENDER_PATH) return { executable: localConfig.BLENDER_PATH, source: '.env.local:BLENDER_PATH (legacy)' };
  const fromPath = spawnSync(process.platform === 'win32' ? 'where.exe' : 'which', ['blender'], { encoding: 'utf8' });
  if (fromPath.status === 0) return { executable: fromPath.stdout.trim().split(/\r?\n/)[0], source: 'PATH' };
  if (process.platform === 'win32') {
    const base = path.join(process.env.ProgramFiles ?? 'C:\\Program Files', 'Blender Foundation');
    if (existsSync(base)) {
      for (const folder of readdirSync(base).sort().reverse()) {
        const candidate = path.join(base, folder, 'blender.exe');
        if (existsSync(candidate)) return { executable: candidate, source: 'standard installation directory' };
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

const blenderDiscovery = discoverBlender();
const blenderPath = blenderDiscovery?.executable;
if (!blenderPath || !existsSync(blenderPath)) {
  report('SKIPPED', 'Blender', 'not found; web development can continue. Set BLENDER_EXECUTABLE or use .env.local.');
} else {
  const version = commandVersion(blenderPath);
  const compatible = version?.includes('4.5.16');
  report(compatible ? 'PASS' : 'FAIL', 'Blender', `${version ?? 'version unavailable'} at ${blenderPath} (${blenderDiscovery.source}); project baseline is 4.5.16`);
  if (!compatible) environmentFailures += 1;
  report('NOT YET TESTED', 'MPFB', 'run the documented Blender preflight; doctor does not modify or open a .blend file');
}

report('NOT YET TESTED', '3D assets', 'run npm run validate:assets; browser playback requires a reviewed GLB');
console.log(`Doctor summary: ${requiredFailures} required failure(s), ${environmentFailures} 3D environment mismatch(es).`);
process.exitCode = requiredFailures + environmentFailures === 0 ? 0 : 1;
