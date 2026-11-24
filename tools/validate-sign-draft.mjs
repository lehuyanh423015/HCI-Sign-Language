import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import validator from 'gltf-validator';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const arg = (name, fallback) => {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
};
const relative = (value) => path.relative(root, value).replaceAll('\\', '/');
const check = (id, passed, actual) => ({ id, status: passed ? 'PASS' : 'FAIL', actual });

function parseGlb(bytes) {
  if (bytes.length < 20 || bytes.toString('ascii', 0, 4) !== 'glTF') throw new Error('invalid GLB magic');
  if (bytes.readUInt32LE(4) !== 2 || bytes.readUInt32LE(8) !== bytes.length) throw new Error('invalid GLB header');
  let offset = 12;
  let document;
  while (offset + 8 <= bytes.length) {
    const length = bytes.readUInt32LE(offset);
    const type = bytes.readUInt32LE(offset + 4);
    if (type === 0x4e4f534a) {
      document = JSON.parse(bytes.subarray(offset + 8, offset + 8 + length).toString('utf8').replace(/\u0000+$/g, '').trim());
    }
    offset += 8 + length;
  }
  if (!document) throw new Error('GLB JSON chunk missing');
  return document;
}

const signId = arg('--sign-id', 'S001');
const expectedClip = arg('--clip', `${signId}_MAIN`);
const assetPath = path.resolve(root, arg('--asset', `assets/exports/signs/${signId}.glb`));
const reportPath = path.resolve(root, arg('--report', `docs/reports/artifacts/${signId}-draft-glb-validation.json`));
const bytes = readFileSync(assetPath);
const document = parseGlb(bytes);
const clips = document.animations ?? [];
const clipNames = clips.map((clip) => clip.name);
const selectedClip = clips.find((clip) => clip.name === expectedClip);
const duration = selectedClip
  ? Math.max(0, ...(selectedClip.samplers ?? []).map((sampler) => document.accessors?.[sampler.input]?.max?.[0] ?? 0))
  : 0;
const nodeNames = new Set((document.nodes ?? []).map((node) => node.name));
const targetNames = new Set((document.meshes ?? []).flatMap((mesh) => mesh.extras?.targetNames ?? []));
const requiredControls = ['upperarm01.L', 'upperarm01.R', 'lowerarm01.L', 'lowerarm01.R', 'wrist.L', 'wrist.R'];
const coreNmm = ['NMM_BROW_RAISE_L', 'NMM_BROW_RAISE_R', 'NMM_EYE_BLINK_L', 'NMM_EYE_BLINK_R', 'NMM_LIPS_ROUND', 'NMM_LIPS_SPREAD'];
const skinJointCounts = (document.skins ?? []).map((skin) => skin.joints?.length ?? 0);
const checks = [
  check('sign_id_format', /^S\d{3}$/.test(signId), signId),
  check('gltf_version', document.asset?.version === '2.0', document.asset?.version),
  check('mesh_count', (document.meshes?.length ?? 0) >= 9, document.meshes?.length ?? 0),
  check('single_skin', (document.skins?.length ?? 0) === 1, document.skins?.length ?? 0),
  check('canonical_joint_count', skinJointCounts.length === 1 && skinJointCounts[0] === 137, skinJointCounts),
  check('single_expected_clip', clipNames.length === 1 && clipNames[0] === expectedClip, clipNames),
  check('positive_clip_duration', duration > 0, { clip: expectedClip, seconds: duration }),
  check('bilateral_arm_controls', requiredControls.every((name) => nodeNames.has(name)), requiredControls.filter((name) => nodeNames.has(name))),
  check('six_core_nmm_targets', coreNmm.every((name) => targetNames.has(name)), coreNmm.filter((name) => targetNames.has(name))),
];
const khronos = await validator.validateBytes(new Uint8Array(bytes), { uri: path.basename(assetPath), maxIssues: 2000 });
checks.push(check('khronos_validator', (khronos.issues?.numErrors ?? 0) === 0, {
  errors: khronos.issues?.numErrors ?? 0,
  warnings: khronos.issues?.numWarnings ?? 0,
  infos: khronos.issues?.numInfos ?? 0,
  hints: khronos.issues?.numHints ?? 0,
}));

const report = {
  schema_version: 1,
  artifact: 'sign_production_candidate_glb_validation',
  status: checks.some((item) => item.status === 'FAIL') ? 'FAIL' : 'PASS',
  classification: 'SIGN_PRODUCTION_CANDIDATE_TECHNICAL_DRAFT',
  linguistic_status: 'NOT YET TESTED',
  sign_id: signId,
  clip: expectedClip,
  asset: {
    path: relative(assetPath),
    sha256: createHash('sha256').update(bytes).digest('hex').toUpperCase(),
    size_bytes: bytes.length,
  },
  checks,
};
mkdirSync(path.dirname(reportPath), { recursive: true });
writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
console.log(`${report.status} sign draft GLB: ${signId} / ${expectedClip}`);
for (const item of checks) console.log(`${item.status} ${item.id}`);
if (report.status !== 'PASS') process.exitCode = 1;
