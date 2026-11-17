import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const manifestPath = path.join(root, 'blender', 'master', 'avatar_master.manifest.json');
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const masterPath = path.resolve(root, manifest.canonical_file);
const bytes = readFileSync(masterPath);
const actual = createHash('sha256').update(bytes).digest('hex').toUpperCase();
if (actual !== manifest.sha256) {
  throw new Error(`canonical master hash mismatch: expected ${manifest.sha256}, got ${actual}`);
}
if (manifest.version !== '1.0.0-rc.1' || manifest.blender_version !== '5.2.4 LTS' || manifest.bone_count !== 137) {
  throw new Error('master manifest contract fields are invalid');
}
console.log(`PASS master manifest: ${manifest.version}, ${manifest.bone_count} bones, SHA-256 ${actual}.`);
