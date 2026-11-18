import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import Ajv2020 from 'ajv/dist/2020.js';
import validator from 'gltf-validator';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const arg = (name, fallback) => {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
};
const relative = (value) => path.relative(root, value).replaceAll('\\', '/');
const check = (id, status, actual) => ({ id, status, actual });
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex').toUpperCase();

function parseGlb(bytes) {
  if (bytes.length < 20 || bytes.toString('ascii', 0, 4) !== 'glTF') throw new Error('invalid GLB magic');
  if (bytes.readUInt32LE(4) !== 2 || bytes.readUInt32LE(8) !== bytes.length) throw new Error('invalid GLB header');
  let offset = 12;
  let document;
  while (offset + 8 <= bytes.length) {
    const length = bytes.readUInt32LE(offset);
    const type = bytes.readUInt32LE(offset + 4);
    if (type === 0x4e4f534a) document = JSON.parse(bytes.subarray(offset + 8, offset + 8 + length).toString('utf8').replace(/\u0000+$/g, '').trim());
    offset += 8 + length;
  }
  if (!document) throw new Error('GLB JSON chunk missing');
  return document;
}

async function inspectGlb(filePath, expectedClips) {
  const bytes = readFileSync(filePath);
  const document = parseGlb(bytes);
  const clips = document.animations ?? [];
  const clipNames = clips.map((clip) => clip.name);
  const durations = clips.map((clip) => ({
    name: clip.name,
    seconds: Math.max(0, ...(clip.samplers ?? []).map((sampler) => document.accessors?.[sampler.input]?.max?.[0] ?? 0)),
  }));
  const targetNames = [...new Set((document.meshes ?? []).flatMap((mesh) => mesh.extras?.targetNames ?? []))];
  const checks = [
    check('gltf_version', document.asset?.version === '2.0' ? 'PASS' : 'FAIL', document.asset?.version),
    check('mesh_and_skin', (document.meshes?.length ?? 0) >= 9 && (document.skins?.length ?? 0) >= 1 ? 'PASS' : 'FAIL', { meshes: document.meshes?.length ?? 0, skins: document.skins?.length ?? 0 }),
    check('expected_clips', expectedClips.every((name) => clipNames.includes(name)) ? 'PASS' : 'FAIL', clipNames),
    check('positive_durations', expectedClips.every((name) => durations.find((row) => row.name === name)?.seconds > 0) ? 'PASS' : 'FAIL', durations),
    check('six_core_nmm_targets', ['NMM_BROW_RAISE_L', 'NMM_BROW_RAISE_R', 'NMM_EYE_BLINK_L', 'NMM_EYE_BLINK_R', 'NMM_LIPS_ROUND', 'NMM_LIPS_SPREAD'].every((name) => targetNames.includes(name)) ? 'PASS' : 'FAIL', targetNames),
  ];
  const khronos = await validator.validateBytes(new Uint8Array(bytes), { uri: path.basename(filePath), maxIssues: 2000 });
  checks.push(check('khronos_validator', (khronos.issues?.numErrors ?? 0) === 0 ? 'PASS' : 'FAIL', {
    errors: khronos.issues?.numErrors ?? 0,
    warnings: khronos.issues?.numWarnings ?? 0,
  }));
  return { path: relative(filePath), sha256: sha256(bytes), size_bytes: bytes.length, clip_names: clipNames, durations, checks };
}

const schemaPath = path.resolve(root, arg('--schema', 'docs/contracts/sign-metadata.schema.json'));
const workspaceRoot = path.resolve(root, arg('--workspace', 'blender/working/signs'));
const reportPath = path.resolve(root, arg('--report', 'docs/reports/artifacts/TASK-0009/sign-package-validation.json'));
const pilotPathArg = arg('--pilot-glb', '');
const ajv = new Ajv2020({
  allErrors: true,
  strict: true,
  formats: {
    uri: /^https?:\/\/[^\s]+$/,
    date: /^\d{4}-\d{2}-\d{2}$/,
  },
});
const validate = ajv.compile(JSON.parse(readFileSync(schemaPath, 'utf8')));
const packages = [];
const allChecks = [];

for (const signId of ['S001', 'S002', 'S003', 'S004', 'S005', 'S006']) {
  const packageDirectory = path.join(workspaceRoot, signId);
  const metadataPath = path.join(packageDirectory, 'sign.json');
  const metadata = JSON.parse(readFileSync(metadataPath, 'utf8'));
  const valid = validate(metadata);
  const checks = [
    check('schema', valid ? 'PASS' : 'FAIL', valid ? 'valid' : validate.errors),
    check('identity_matches_directory', metadata.identity.sign_id === signId ? 'PASS' : 'FAIL', metadata.identity.sign_id),
    check('source_reference', metadata.reference.source_verification_status === 'PASS' ? 'PASS' : 'NOT YET TESTED', metadata.reference.source_verification_status),
  ];
  const productionRequired = ['IN_PRODUCTION', 'TECHNICAL_REVIEW', 'LINGUISTIC_REVIEW', 'APPROVED'].includes(metadata.identity.status);
  for (const [id, field] of [['blender_source', 'animation_file'], ['glb_export', 'export_file'], ['preview', 'preview_file']]) {
    const configured = metadata.production[field];
    const present = Boolean(configured && existsSync(path.join(root, ...configured.split('/'))));
    checks.push(check(id, present ? 'PASS' : productionRequired ? 'FAIL' : 'NOT YET TESTED', configured));
  }
  const approvalSafe = metadata.identity.status !== 'APPROVED' || (
    metadata.reference.source_verification_status === 'PASS'
    && metadata.review.technical_review_status === 'PASS'
    && metadata.review.linguistic_review_status === 'PASS'
  );
  checks.push(check('no_accidental_approval', approvalSafe ? 'PASS' : 'FAIL', metadata.identity.status));
  packages.push({ sign_id: signId, path: relative(metadataPath), status: checks.some((item) => item.status === 'FAIL') ? 'FAIL' : 'PASS', checks });
  allChecks.push(...checks.map((item) => ({ ...item, id: `${signId}_${item.id}` })));
}

let pilot = null;
if (pilotPathArg) {
  const pilotPath = path.resolve(root, pilotPathArg);
  pilot = await inspectGlb(pilotPath, [arg('--pilot-clip', 'TECH_HAND_FACE_TEST')]);
  pilot.classification = 'TECHNICAL_FIXTURE_NOT_A_SIGN';
  pilot.linguistic_status = 'NOT YET TESTED';
  allChecks.push(...pilot.checks.map((item) => ({ ...item, id: `pilot_${item.id}` })));
}

const report = {
  schema_version: 1,
  artifact: 'task0009_sign_package_validation',
  status: allChecks.some((item) => item.status === 'FAIL') ? 'FAIL' : 'PASS',
  placeholder_packages: packages,
  pilot,
  actual_sign_pilot: { status: 'BLOCKED', reason: 'No verified owner-provided VSL reference exists for S001-S006.' },
  checks: allChecks,
};
mkdirSync(path.dirname(reportPath), { recursive: true });
writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
for (const item of packages) console.log(`${item.status} sign package schema: ${item.sign_id}`);
if (pilot) console.log(`${pilot.checks.some((item) => item.status === 'FAIL') ? 'FAIL' : 'PASS'} technical fixture GLB: ${pilot.path}`);
console.log(`${report.status} TASK-0009 sign package validation (${readdirSync(workspaceRoot).length} workspace entries)`);
if (report.status !== 'PASS') process.exitCode = 1;
