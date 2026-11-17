import { existsSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const signs = JSON.parse(readFileSync(path.join(projectRoot, 'data', 'signs.json'), 'utf8'));
const signatures = new Map();
let failures = 0;
let validated = 0;

function inspectGlb(filePath, expectedClip) {
  const bytes = readFileSync(filePath);
  if (bytes.length < 20 || bytes.toString('ascii', 0, 4) !== 'glTF') throw new Error('invalid GLB magic header');
  if (bytes.readUInt32LE(4) !== 2) throw new Error('GLB must use glTF 2.0');
  if (bytes.readUInt32LE(8) !== bytes.length) throw new Error('declared GLB length does not match file size');
  const jsonLength = bytes.readUInt32LE(12);
  if (bytes.readUInt32LE(16) !== 0x4e4f534a) throw new Error('first GLB chunk is not JSON');
  const document = JSON.parse(bytes.toString('utf8', 20, 20 + jsonLength).replace(/\u0000+$/g, '').trim());
  const animations = document.animations ?? [];
  if (!animations.some((animation) => animation.name === expectedClip)) throw new Error(`missing animation clip ${expectedClip}`);
  if (!document.meshes?.length) throw new Error('missing mesh data');
  if (!document.skins?.length) throw new Error('missing skinning data');
  const nodes = document.nodes ?? [];
  const parentByChild = new Map();
  nodes.forEach((node, parent) => (node.children ?? []).forEach((child) => parentByChild.set(child, parent)));
  const joints = [...new Set(document.skins.flatMap((skin) => skin.joints ?? []))].sort((a, b) => a - b);
  const hierarchy = joints.map((index) => ({
    name: nodes[index]?.name ?? `#${index}`,
    parent: parentByChild.has(index) ? (nodes[parentByChild.get(index)]?.name ?? `#${parentByChild.get(index)}`) : null,
  }));
  return createHash('sha256').update(JSON.stringify(hierarchy)).digest('hex');
}

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
