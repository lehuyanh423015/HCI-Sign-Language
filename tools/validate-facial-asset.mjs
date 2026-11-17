import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import validator from 'gltf-validator';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function argument(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
}

const assetPath = path.resolve(root, argument('--asset', 'assets/exports/technical/technical-facial-test.glb'));
const reportPath = path.resolve(root, argument('--report', 'docs/reports/artifacts/TASK-0006/glb-validation.json'));
const expectedTargets = ['NMM_BROW_RAISE_L', 'NMM_BROW_RAISE_R', 'NMM_EYE_BLINK_L', 'NMM_EYE_BLINK_R', 'NMM_LIPS_ROUND', 'NMM_LIPS_SPREAD'];
const expectedClips = ['NMM_BLINK_TEST', 'NMM_BROW_TEST', 'NMM_MOUTH_TEST', 'TECH_HAND_FACE_TEST'];
const expectedEyes = ['NMM_Eyeball.L', 'NMM_Iris.L', 'NMM_Pupil.L', 'NMM_Eyeball.R', 'NMM_Iris.R', 'NMM_Pupil.R'];

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

const bytes = readFileSync(assetPath);
const document = parseGlb(bytes);
const nodeNames = (document.nodes ?? []).map((node) => node.name).filter(Boolean);
const targetNames = [...new Set((document.meshes ?? []).flatMap((mesh) => mesh.extras?.targetNames ?? []))];
const animations = document.animations ?? [];
const clipNames = animations.map((animation) => animation.name);
const channels = animations.flatMap((animation) => (animation.channels ?? []).map((channel) => ({
  animation: animation.name,
  path: channel.target.path,
  node: document.nodes?.[channel.target.node]?.name ?? `#${channel.target.node}`,
})));
const combinedChannels = channels.filter((channel) => channel.animation === 'TECH_HAND_FACE_TEST');
const durationRows = animations.map((animation) => {
  const times = (animation.samplers ?? []).map((sampler) => document.accessors?.[sampler.input]?.max?.[0] ?? 0);
  return { name: animation.name, duration_seconds: Math.max(0, ...times) };
});
const check = (id, passed, actual) => ({ id, status: passed ? 'PASS' : 'FAIL', actual });
const checks = [
  check('gltf_version', document.asset?.version === '2.0', document.asset?.version),
  check('mesh_count', (document.meshes?.length ?? 0) >= 9, document.meshes?.length ?? 0),
  check('skin', (document.skins?.length ?? 0) >= 1, document.skins?.length ?? 0),
  check('eye_nodes', expectedEyes.every((name) => nodeNames.includes(name)), expectedEyes.filter((name) => nodeNames.includes(name))),
  check('nmm_targets', expectedTargets.every((name) => targetNames.includes(name)), targetNames),
  check('no_task0005_diagnostic_target', !targetNames.includes('TASK0005_DIAGNOSTIC_MORPH'), targetNames),
  check('clip_names', expectedClips.every((name) => clipNames.includes(name)), clipNames),
  check('positive_clip_durations', durationRows.every((row) => row.duration_seconds > 0), durationRows),
  check('morph_weight_animation', channels.some((channel) => channel.path === 'weights'), channels.filter((channel) => channel.path === 'weights')),
  check('combined_weight_channel', combinedChannels.some((channel) => channel.path === 'weights'), combinedChannels.filter((channel) => channel.path === 'weights')),
  check('combined_hand_channels', combinedChannels.some((channel) => channel.node?.startsWith('finger') && channel.node.endsWith('.R')), combinedChannels.filter((channel) => channel.node?.startsWith('finger'))),
  check('combined_head_jaw_eye_channels', ['head', 'jaw', 'eye.L', 'eye.R'].every((name) => combinedChannels.some((channel) => channel.node === name)), combinedChannels.filter((channel) => ['head', 'jaw', 'eye.L', 'eye.R'].includes(channel.node))),
];

const validation = await validator.validateBytes(new Uint8Array(bytes), { uri: path.basename(assetPath), maxIssues: 2000 });
checks.push(check('khronos_validator', (validation.issues?.numErrors ?? 0) === 0, {
  errors: validation.issues?.numErrors ?? 0,
  warnings: validation.issues?.numWarnings ?? 0,
  infos: validation.issues?.numInfos ?? 0,
  hints: validation.issues?.numHints ?? 0,
}));

const report = {
  schema_version: 1,
  artifact: path.relative(root, assetPath).replaceAll('\\', '/'),
  technical_fixture_only: true,
  linguistic_status: 'NOT YET TESTED',
  sha256: createHash('sha256').update(bytes).digest('hex').toUpperCase(),
  size_bytes: bytes.length,
  status: checks.every((item) => item.status === 'PASS') ? 'PASS' : 'FAIL',
  structural: {
    generator: document.asset?.generator,
    nodes: document.nodes?.length ?? 0,
    meshes: document.meshes?.length ?? 0,
    skins: document.skins?.length ?? 0,
    materials: document.materials?.length ?? 0,
    morph_target_names: targetNames,
    animation_durations: durationRows,
    animation_channel_counts: animations.map((animation) => ({ name: animation.name, channels: animation.channels?.length ?? 0 })),
  },
  checks,
  khronos_validator: {
    num_errors: validation.issues?.numErrors ?? 0,
    num_warnings: validation.issues?.numWarnings ?? 0,
    num_infos: validation.issues?.numInfos ?? 0,
    num_hints: validation.issues?.numHints ?? 0,
    messages: validation.issues?.messages ?? [],
  },
};

mkdirSync(path.dirname(reportPath), { recursive: true });
writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
for (const item of checks) console.log(`${item.status} facial GLB: ${item.id}`);
console.log(`${report.status} facial GLB: ${report.artifact}`);
if (report.status !== 'PASS') process.exitCode = 1;
