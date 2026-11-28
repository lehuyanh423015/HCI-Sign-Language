import { existsSync, readFileSync } from 'node:fs';
import { inspectGlb } from './inspect-glb.mjs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const signs = JSON.parse(readFileSync(path.join(projectRoot, 'data', 'signs.json'), 'utf8'));
const signatures = new Map();
let failures = 0;
let validated = 0;

for (const sign of signs) {
  const published = path.join(projectRoot, 'apps', 'web', 'public', ...sign.glbPath.split('/'));
  const stagedExport = path.join(projectRoot, 'assets', 'exports', 'signs', `${sign.id}.glb`);
  const filePath = [published, stagedExport].find(existsSync);
  if (!filePath) {
    const status = sign.reviewStatus === 'approved' ? 'FAIL' : 'NOT YET TESTED';
    console.log(`${status} ${sign.id}: pending GLB (${sign.glbPath})`);
    if (status === 'FAIL') failures += 1;
    continue;
  }
  try {
    const signature = inspectGlb(filePath, sign.animationClip);
    signatures.set(sign.id, signature);
    validated += 1;
    console.log(`PASS ${sign.id}: GLB structure, mesh, skin and clip ${sign.animationClip} found.`);
  } catch (error) {
    failures += 1;
    console.error(`FAIL ${sign.id}: ${error.message}`);
  }
}

if (new Set(signatures.values()).size > 1) {
  failures += 1;
  console.error('FAIL rig: exported signs have different joint-name/hierarchy signatures.');
} else if (signatures.size > 0) {
  console.log('PASS rig: all inspected exports share one joint-name/hierarchy signature.');
} else {
  console.log('NOT YET TESTED rig: no GLB exists; browser playback and manual visual QA remain pending.');
}

console.log(`Asset summary: ${validated} validated, ${signs.length - validated} pending, ${failures} failed.`);
process.exitCode = failures === 0 ? 0 : 1;
