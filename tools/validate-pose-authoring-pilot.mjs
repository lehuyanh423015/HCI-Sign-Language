import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import validator from 'gltf-validator';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argument = (name, fallback) => {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
};
const assetPath = path.resolve(root, argument('--asset', 'assets/exports/technical/task-0010/tech-pose-authoring-pilot.glb'));
const reportPath = path.resolve(root, argument('--report', 'docs/reports/artifacts/TASK-0010/glb-validation.json'));

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
const nodeNames = (document.nodes ?? []).map((node) => node.name ?? null);
const animations = document.animations ?? [];
const clipNames = animations.map((animation) => animation.name);
const targetNames = [...new Set((document.meshes ?? []).flatMap((mesh) => mesh.extras?.targetNames ?? []))];
const channels = animations.flatMap((animation) => (animation.channels ?? []).map((channel) => ({
  clip: animation.name,
  path: channel.target.path,
  node: nodeNames[channel.target.node] ?? `#${channel.target.node}`,
})));
const durationRows = animations.map((animation) => ({
  name: animation.name,
  seconds: Math.max(0, ...(animation.samplers ?? []).map((sampler) => document.accessors?.[sampler.input]?.max?.[0] ?? 0)),
}));
const expectedTargets = ['NMM_BROW_RAISE_L', 'NMM_BROW_RAISE_R', 'NMM_EYE_BLINK_L', 'NMM_EYE_BLINK_R', 'NMM_LIPS_ROUND', 'NMM_LIPS_SPREAD'];
const expectedBoneNodes = [
  ...['L', 'R'].flatMap((side) => [
    ...Array.from({ length: 5 }, (_, family) => Array.from({ length: 3 }, (_, segment) => `finger${family + 1}-${segment + 1}.${side}`)).flat(),
    `wrist.${side}`, `upperarm01.${side}`, `lowerarm01.${side}`,
  ]),
  'head', 'neck02', 'jaw',
];
const expectedEyes = ['NMM_Eyeball.L', 'NMM_Iris.L', 'NMM_Pupil.L', 'NMM_Eyeball.R', 'NMM_Iris.R', 'NMM_Pupil.R'];
const pilotChannels = channels.filter((channel) => channel.clip === 'TECH_POSE_AUTHORING_PILOT');
const check = (id, passed, actual) => ({ id, status: passed ? 'PASS' : 'FAIL', actual });
const checks = [
  check('gltf_version', document.asset?.version === '2.0', document.asset?.version),
  check('mesh_count', (document.meshes?.length ?? 0) === 9, document.meshes?.length ?? 0),
  check('single_skin', (document.skins?.length ?? 0) === 1, document.skins?.length ?? 0),
  check('canonical_joint_count', document.skins?.[0]?.joints?.length === 137, document.skins?.[0]?.joints?.length ?? 0),
  check('single_expected_clip', clipNames.length === 1 && clipNames[0] === 'TECH_POSE_AUTHORING_PILOT', clipNames),
  check('positive_duration', durationRows.length === 1 && durationRows[0].seconds > 0, durationRows),
  check('both_hand_nodes', expectedBoneNodes.every((name) => nodeNames.includes(name)), expectedBoneNodes.filter((name) => !nodeNames.includes(name))),
  check('eye_nodes', expectedEyes.every((name) => nodeNames.includes(name)), expectedEyes.filter((name) => nodeNames.includes(name))),
  check('six_core_nmm_targets', expectedTargets.every((name) => targetNames.includes(name)), targetNames),
  check('both_hand_animation_channels', ['L', 'R'].every((side) => pilotChannels.some((channel) => channel.node?.startsWith('finger') && channel.node.endsWith(`.${side}`))), pilotChannels.filter((channel) => channel.node?.startsWith('finger'))),
  check('wrist_arm_channels', ['wrist.L', 'wrist.R', 'upperarm01.L', 'upperarm01.R', 'lowerarm01.L', 'lowerarm01.R'].every((name) => pilotChannels.some((channel) => channel.node === name)), pilotChannels.filter((channel) => channel.node?.includes('arm') || channel.node?.startsWith('wrist'))),
  check('head_neck_jaw_channels', ['head', 'neck02', 'jaw'].every((name) => pilotChannels.some((channel) => channel.node === name)), pilotChannels.filter((channel) => ['head', 'neck02', 'jaw'].includes(channel.node))),
  check('morph_weight_channel', pilotChannels.some((channel) => channel.path === 'weights'), pilotChannels.filter((channel) => channel.path === 'weights')),
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
  artifact: 'task0010_pose_authoring_pilot_glb_validation',
  classification: 'TECHNICAL_FIXTURE_NOT_A_SIGN',
  linguistic_status: 'NOT_APPLICABLE',
  status: checks.every((item) => item.status === 'PASS') ? 'PASS' : 'FAIL',
  path: path.relative(root, assetPath).replaceAll('\\', '/'),
  sha256: createHash('sha256').update(bytes).digest('hex').toUpperCase(),
  size_bytes: bytes.length,
  structural: {
    nodes: document.nodes?.length ?? 0,
    meshes: document.meshes?.length ?? 0,
    skins: document.skins?.length ?? 0,
    joints: document.skins?.[0]?.joints?.length ?? 0,
    clip_names: clipNames,
    durations: durationRows,
    channel_count: pilotChannels.length,
    morph_target_names: targetNames,
  },
  checks,
  khronos: validation.issues,
};
mkdirSync(path.dirname(reportPath), { recursive: true });
writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
for (const item of checks) console.log(`${item.status} pose pilot GLB: ${item.id}`);
console.log(`${report.status} pose pilot GLB: ${report.path}`);
if (report.status !== 'PASS') process.exitCode = 1;
