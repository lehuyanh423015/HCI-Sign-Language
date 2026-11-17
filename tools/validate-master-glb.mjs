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

const profile = argument('--profile', 'MASTER_STATIC');
const assetPath = path.resolve(root, argument('--asset', 'assets/exports/master/avatar-master-v1-rc1.glb'));
const reportPath = path.resolve(root, argument('--report', 'docs/reports/artifacts/TASK-0005-master-static-validation.json'));
if (!['MASTER_STATIC', 'MORPH_POC'].includes(profile)) throw new Error(`unsupported profile ${profile}`);

function parseGlb(bytes) {
  if (bytes.length < 20 || bytes.toString('ascii', 0, 4) !== 'glTF') throw new Error('invalid GLB magic');
  if (bytes.readUInt32LE(4) !== 2) throw new Error('GLB version is not 2');
  if (bytes.readUInt32LE(8) !== bytes.length) throw new Error('declared GLB length differs from file size');
  let offset = 12;
  let document;
  while (offset + 8 <= bytes.length) {
    const length = bytes.readUInt32LE(offset);
    const type = bytes.readUInt32LE(offset + 4);
    const chunk = bytes.subarray(offset + 8, offset + 8 + length);
    if (type === 0x4e4f534a) document = JSON.parse(chunk.toString('utf8').replace(/\u0000+$/g, '').trim());
    offset += 8 + length;
  }
  if (!document) throw new Error('GLB JSON chunk is missing');
  return document;
}

const bytes = readFileSync(assetPath);
const document = parseGlb(bytes);
const animations = document.animations ?? [];
const primitives = (document.meshes ?? []).flatMap((mesh, meshIndex) =>
  (mesh.primitives ?? []).map((primitive, primitiveIndex) => ({ meshIndex, primitiveIndex, primitive })),
);
const morphTargetCount = primitives.reduce((sum, row) => sum + (row.primitive.targets?.length ?? 0), 0);
const morphTargetNames = (document.meshes ?? []).flatMap((mesh) => mesh.extras?.targetNames ?? []);
const channels = animations.flatMap((animation) =>
  (animation.channels ?? []).map((channel) => ({
    animation: animation.name,
    path: channel.target.path,
    node: document.nodes?.[channel.target.node]?.name ?? `#${channel.target.node}`,
  })),
);
const weightChannels = channels.filter((channel) => channel.path === 'weights');
const rotationChannels = channels.filter((channel) => channel.path === 'rotation');

const checks = [
  { id: 'gltf_version', status: document.asset?.version === '2.0' ? 'PASS' : 'FAIL', actual: document.asset?.version },
  { id: 'meshes', status: (document.meshes?.length ?? 0) >= 3 ? 'PASS' : 'FAIL', actual: document.meshes?.length ?? 0 },
  { id: 'skin', status: (document.skins?.length ?? 0) >= 1 ? 'PASS' : 'FAIL', actual: document.skins?.length ?? 0 },
];

if (profile === 'MASTER_STATIC') {
  checks.push(
    { id: 'no_animation', status: animations.length === 0 ? 'PASS' : 'FAIL', actual: animations.map((item) => item.name) },
    { id: 'no_morph_targets', status: morphTargetCount === 0 ? 'PASS' : 'FAIL', actual: morphTargetCount },
  );
} else {
  checks.push(
    { id: 'static_morph_target', status: morphTargetCount > 0 ? 'PASS' : 'FAIL', actual: morphTargetCount },
    { id: 'diagnostic_target_name', status: morphTargetNames.includes('TASK0005_DIAGNOSTIC_MORPH') ? 'PASS' : 'FAIL', actual: morphTargetNames },
    { id: 'animated_morph_weights', status: weightChannels.length > 0 ? 'PASS' : 'FAIL', actual: weightChannels },
    { id: 'bone_rotation_animation', status: rotationChannels.length > 0 ? 'PASS' : 'FAIL', actual: rotationChannels.length },
    { id: 'technical_action_present', status: animations.some((item) => item.name === 'TECH_HAND_CONTROL_TEST') ? 'PASS' : 'FAIL', actual: animations.map((item) => item.name) },
  );
}

const validation = await validator.validateBytes(new Uint8Array(bytes), {
  uri: path.basename(assetPath),
  maxIssues: 1000,
});
checks.push({
  id: 'khronos_validator',
  status: (validation.issues?.numErrors ?? 0) === 0 ? 'PASS' : 'FAIL',
  actual: {
    errors: validation.issues?.numErrors ?? 0,
    warnings: validation.issues?.numWarnings ?? 0,
    infos: validation.issues?.numInfos ?? 0,
    hints: validation.issues?.numHints ?? 0,
  },
});

const result = {
  schema_version: 1,
  profile,
  artifact: path.relative(root, assetPath).replaceAll('\\', '/'),
  sha256: createHash('sha256').update(bytes).digest('hex').toUpperCase(),
  size_bytes: bytes.length,
  status: checks.every((check) => check.status === 'PASS') ? 'PASS' : 'FAIL',
  structural: {
    generator: document.asset?.generator,
    nodes: document.nodes?.length ?? 0,
    meshes: document.meshes?.length ?? 0,
    primitives: primitives.length,
    skins: document.skins?.length ?? 0,
    materials: document.materials?.length ?? 0,
    animations: animations.map((item) => item.name),
    morph_target_count: morphTargetCount,
    morph_target_names: morphTargetNames,
    weight_animation_channels: weightChannels,
    rotation_animation_channel_count: rotationChannels.length,
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
writeFileSync(reportPath, `${JSON.stringify(result, null, 2)}\n`, 'utf8');
for (const check of checks) console.log(`${check.status} ${profile}: ${check.id}`);
console.log(`${result.status} ${profile}: ${result.artifact}`);
if (result.status !== 'PASS') process.exitCode = 1;
