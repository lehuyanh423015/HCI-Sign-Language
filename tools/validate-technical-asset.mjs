import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import validator from 'gltf-validator';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const assetPath = path.join(root, 'assets', 'exports', 'technical', 'technical-hand-test.glb');
const expectedClip = 'TECH_HAND_CONTROL_TEST';
const expectedBones = new Set(Array.from({ length: 5 }, (_, digit) =>
  Array.from({ length: 3 }, (_, joint) => `finger${digit + 1}-${joint + 1}.R`),
).flat());
const reportIndex = process.argv.indexOf('--report');
const reportPath = reportIndex >= 0 && process.argv[reportIndex + 1]
  ? path.resolve(root, process.argv[reportIndex + 1])
  : null;

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
const animation = animations.find((candidate) => candidate.name === expectedClip);
if (!animation) throw new Error(`expected animation ${expectedClip} was not found`);
if (!document.meshes?.length) throw new Error('mesh data is missing');
if (!document.skins?.length) throw new Error('skin data is missing');

const targetNames = animation.channels.map((channel) => document.nodes?.[channel.target.node]?.name ?? `#${channel.target.node}`);
const unexpectedTargets = [...new Set(targetNames.filter((name) => !expectedBones.has(name)))].sort();
const animatedBones = [...new Set(targetNames)].sort();
const missingBones = [...expectedBones].filter((name) => !animatedBones.includes(name)).sort();
if (unexpectedTargets.length) throw new Error(`unexpected animation targets: ${unexpectedTargets.join(', ')}`);
if (missingBones.length) throw new Error(`expected finger animation targets missing: ${missingBones.join(', ')}`);

const inputAccessors = animation.samplers.map((sampler) => document.accessors?.[sampler.input]).filter(Boolean);
const duration = Math.max(...inputAccessors.map((accessor) => accessor.max?.[0] ?? 0));
if (!(duration >= 0.9 && duration <= 1.1)) throw new Error(`animation duration ${duration} is outside 0.9–1.1 seconds`);

const validation = await validator.validateBytes(new Uint8Array(bytes), {
  uri: 'technical-hand-test.glb',
  maxIssues: 1000,
});
const severityCounts = validation.issues?.numErrors ?? 0;
if (severityCounts > 0) throw new Error(`Khronos validator reported ${severityCounts} error(s)`);

const result = {
  schema_version: 1,
  artifact: path.relative(root, assetPath).replaceAll('\\', '/'),
  sha256: createHash('sha256').update(bytes).digest('hex').toUpperCase(),
  size_bytes: bytes.length,
  status: 'PASS',
  structural: {
    gltf_version: document.asset?.version,
    generator: document.asset?.generator,
    scenes: document.scenes?.length ?? 0,
    nodes: document.nodes?.length ?? 0,
    meshes: document.meshes.length,
    skins: document.skins.length,
    materials: document.materials?.length ?? 0,
    textures: document.textures?.length ?? 0,
    animations: animations.map((item) => item.name),
  },
  animation: {
    name: animation.name,
    duration_seconds: duration,
    channel_count: animation.channels.length,
    sampler_count: animation.samplers.length,
    target_bones: animatedBones,
    unexpected_targets: unexpectedTargets,
    missing_expected_bones: missingBones,
  },
  khronos_validator: {
    num_errors: validation.issues?.numErrors ?? 0,
    num_warnings: validation.issues?.numWarnings ?? 0,
    num_infos: validation.issues?.numInfos ?? 0,
    num_hints: validation.issues?.numHints ?? 0,
    messages: validation.issues?.messages ?? [],
  },
};

if (reportPath) {
  mkdirSync(path.dirname(reportPath), { recursive: true });
  writeFileSync(reportPath, `${JSON.stringify(result, null, 2)}\n`, 'utf8');
}
console.log(`PASS technical GLB: ${result.structural.meshes} mesh, ${result.structural.skins} skin, ${animation.name}, ${duration.toFixed(4)}s, ${animation.channels.length} channels.`);
console.log(`PASS Khronos validator: 0 errors, ${result.khronos_validator.num_warnings} warning(s).`);
