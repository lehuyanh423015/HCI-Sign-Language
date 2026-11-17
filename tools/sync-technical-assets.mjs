import { copyFileSync, existsSync, mkdirSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.join(root, 'assets', 'exports', 'technical', 'technical-hand-test.glb');
const destination = path.join(root, 'apps', 'web', 'public', 'models', 'technical', 'technical-hand-test.glb');
const checkOnly = process.argv.includes('--check');

function sha256(filePath) {
  return createHash('sha256').update(readFileSync(filePath)).digest('hex');
}

if (!existsSync(source)) {
  console.error(`FAIL technical sync: canonical GLB is missing: ${source}`);
  process.exitCode = 1;
} else if (checkOnly) {
  if (!existsSync(destination)) {
    console.error('FAIL technical sync: generated web copy is missing; run npm run sync:technical-assets.');
    process.exitCode = 1;
  } else if (sha256(source) !== sha256(destination)) {
    console.error('FAIL technical sync: generated web copy does not match canonical GLB.');
    process.exitCode = 1;
  } else {
    console.log(`PASS technical sync: web copy matches canonical GLB (${sha256(source)}).`);
  }
} else {
  mkdirSync(path.dirname(destination), { recursive: true });
  copyFileSync(source, destination);
  console.log(`PASS technical sync: copied canonical GLB to ${path.relative(root, destination)}.`);
}
