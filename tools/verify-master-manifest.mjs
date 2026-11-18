import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const manifestPath = path.join(root, 'blender', 'master', 'master-avatar.manifest.json');
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const masterPath = path.resolve(root, manifest.canonical_source.path);
const bytes = readFileSync(masterPath);
const actual = createHash('sha256').update(bytes).digest('hex').toUpperCase();
if (actual !== manifest.canonical_source.sha256) {
  throw new Error(`canonical master hash mismatch: expected ${manifest.canonical_source.sha256}, got ${actual}`);
}
if (
  manifest.version !== '1.0.0'
  || manifest.release_status !== 'Temporary Technical Release'
  || manifest.blender_version !== '5.2.4 LTS'
  || manifest.rig?.bone_count !== 137
  || manifest.approval?.technical_validation !== 'PASS'
  || manifest.approval?.owner_visual !== 'APPROVED'
  || manifest.approval?.vietnamese_sign_language !== 'NOT YET TESTED'
) {
  throw new Error('master manifest contract fields are invalid');
}
console.log(`PASS master manifest: ${manifest.version}, ${manifest.rig.bone_count} bones, SHA-256 ${actual}.`);
