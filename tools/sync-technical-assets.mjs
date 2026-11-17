import { copyFileSync, existsSync, mkdirSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const filenames = ['technical-hand-test.glb', 'technical-hand-test-neutral.glb'];
const checkOnly = process.argv.includes('--check');

function sha256(filePath) {
  return createHash('sha256').update(readFileSync(filePath)).digest('hex');
}

for (const filename of filenames) {
  const source = path.join(root, 'assets', 'exports', 'technical', filename);
  const destination = path.join(root, 'apps', 'web', 'public', 'models', 'technical', filename);
  if (!existsSync(source)) {
    console.error(`FAIL technical sync: canonical GLB is missing: ${source}`);
    process.exitCode = 1;
  } else if (checkOnly) {
    if (!existsSync(destination)) {
      console.error(`FAIL technical sync: generated web copy is missing for ${filename}; run npm run sync:technical-assets.`);
      process.exitCode = 1;
    } else if (sha256(source) !== sha256(destination)) {
      console.error(`FAIL technical sync: generated web copy does not match canonical GLB for ${filename}.`);
      process.exitCode = 1;
    } else {
      console.log(`PASS technical sync: ${filename} matches canonical GLB (${sha256(source)}).`);
    }
  } else {
    mkdirSync(path.dirname(destination), { recursive: true });
    copyFileSync(source, destination);
    console.log(`PASS technical sync: copied ${filename} to ${path.relative(root, destination)}.`);
  }
}
