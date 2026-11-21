import { copyFileSync, existsSync, mkdirSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const assets = [
  { source: 'assets/exports/technical/technical-hand-test.glb', destination: 'technical-hand-test.glb' },
  { source: 'assets/exports/technical/technical-hand-test-neutral.glb', destination: 'technical-hand-test-neutral.glb' },
  { source: 'assets/exports/technical/technical-facial-test.glb', destination: 'technical-facial-test.glb' },
  {
    source: 'assets/exports/technical/task-0007a/technical-facial-refined-test.glb',
    destination: 'master-avatar-v1-technical-demo.glb',
  },
  {
    source: 'assets/exports/technical/task-0009/technical-sign-pipeline-pilot.glb',
    destination: 'technical-sign-pipeline-pilot.glb',
  },
  {
    source: 'assets/exports/technical/task-0010/tech-pose-authoring-pilot.glb',
    destination: 'tech-pose-authoring-pilot.glb',
  },
];
const checkOnly = process.argv.includes('--check');

function sha256(filePath) {
  return createHash('sha256').update(readFileSync(filePath)).digest('hex');
}

for (const asset of assets) {
  const source = path.join(root, ...asset.source.split('/'));
  const destination = path.join(root, 'apps', 'web', 'public', 'models', 'technical', asset.destination);
  if (!existsSync(source)) {
    console.error(`FAIL technical sync: canonical GLB is missing: ${source}`);
    process.exitCode = 1;
  } else if (checkOnly) {
    if (!existsSync(destination)) {
      console.error(`FAIL technical sync: generated web copy is missing for ${asset.destination}; run npm run sync:technical-assets.`);
      process.exitCode = 1;
    } else if (sha256(source) !== sha256(destination)) {
      console.error(`FAIL technical sync: generated web copy does not match canonical GLB for ${asset.destination}.`);
      process.exitCode = 1;
    } else {
      console.log(`PASS technical sync: ${asset.destination} matches ${asset.source} (${sha256(source)}).`);
    }
  } else {
    mkdirSync(path.dirname(destination), { recursive: true });
    copyFileSync(source, destination);
    console.log(`PASS technical sync: copied ${asset.source} to ${path.relative(root, destination)}.`);
  }
}
