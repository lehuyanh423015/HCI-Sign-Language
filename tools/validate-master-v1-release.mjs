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

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex').toUpperCase();
}

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

const staticPath = path.resolve(root, argument('--static', 'assets/releases/master-avatar-v1/master-avatar-v1-static.glb'));
const technicalPath = path.resolve(root, argument('--technical', 'assets/exports/technical/task-0007a/technical-facial-refined-test.glb'));
const releaseManifestPath = path.resolve(root, argument('--manifest', 'assets/releases/master-avatar-v1/release-manifest.json'));
const masterManifestPath = path.resolve(root, argument('--master-manifest', 'blender/master/master-avatar.manifest.json'));
const reportPath = path.resolve(root, argument('--report', 'docs/reports/artifacts/TASK-0008/master-v1-glb-validation.json'));

const expectedTargets = ['NMM_BROW_RAISE_L', 'NMM_BROW_RAISE_R', 'NMM_EYE_BLINK_L', 'NMM_EYE_BLINK_R', 'NMM_LIPS_ROUND', 'NMM_LIPS_SPREAD'];
const expectedClips = ['NMM_BLINK_TEST', 'NMM_BROW_TEST', 'NMM_MOUTH_TEST', 'TECH_HAND_FACE_TEST'];
const expectedEyes = ['NMM_Eyeball.L', 'NMM_Iris.L', 'NMM_Pupil.L', 'NMM_Eyeball.R', 'NMM_Iris.R', 'NMM_Pupil.R'];
const check = (id, passed, actual) => ({ id, status: passed ? 'PASS' : 'FAIL', actual });

async function inspectGlb(filePath, profile) {
  const bytes = readFileSync(filePath);
  const document = parseGlb(bytes);
  const nodeNames = (document.nodes ?? []).map((node) => node.name).filter(Boolean);
  const targetNames = [...new Set((document.meshes ?? []).flatMap((mesh) => mesh.extras?.targetNames ?? []))];
  const clipNames = (document.animations ?? []).map((animation) => animation.name);
  const checks = [
    check(`${profile}_gltf_version`, document.asset?.version === '2.0', document.asset?.version),
    check(`${profile}_mesh_count`, (document.meshes?.length ?? 0) >= 9, document.meshes?.length ?? 0),
    check(`${profile}_skin`, (document.skins?.length ?? 0) >= 1, document.skins?.length ?? 0),
    check(`${profile}_eye_nodes`, expectedEyes.every((name) => nodeNames.includes(name)), expectedEyes.filter((name) => nodeNames.includes(name))),
    check(`${profile}_nmm_targets`, expectedTargets.every((name) => targetNames.includes(name)), targetNames),
    check(`${profile}_no_diagnostic_target`, !targetNames.includes('TASK0005_DIAGNOSTIC_MORPH'), targetNames),
  ];
  if (profile === 'static') {
    checks.push(check('static_no_animations', clipNames.length === 0, clipNames));
  } else {
    checks.push(check('technical_clip_names', expectedClips.every((name) => clipNames.includes(name)), clipNames));
  }
  const khronos = await validator.validateBytes(new Uint8Array(bytes), { uri: path.basename(filePath), maxIssues: 2000 });
  checks.push(check(`${profile}_khronos`, (khronos.issues?.numErrors ?? 0) === 0, {
    errors: khronos.issues?.numErrors ?? 0,
    warnings: khronos.issues?.numWarnings ?? 0,
    infos: khronos.issues?.numInfos ?? 0,
    hints: khronos.issues?.numHints ?? 0,
  }));
  return {
    path: path.relative(root, filePath).replaceAll('\\', '/'),
    sha256: sha256(bytes),
    size_bytes: bytes.length,
    nodes: document.nodes?.length ?? 0,
    meshes: document.meshes?.length ?? 0,
    skins: document.skins?.length ?? 0,
    morph_target_names: targetNames,
    animation_clip_names: clipNames,
    checks,
    khronos: khronos.issues,
  };
}

const staticAsset = await inspectGlb(staticPath, 'static');
const technicalAsset = await inspectGlb(technicalPath, 'technical');
const releaseManifest = JSON.parse(readFileSync(releaseManifestPath, 'utf8'));
const masterManifest = JSON.parse(readFileSync(masterManifestPath, 'utf8'));
const checks = [
  ...staticAsset.checks,
  ...technicalAsset.checks,
  check('release_version', releaseManifest.version === '1.0.0' && masterManifest.version === '1.0.0', { release: releaseManifest.version, master: masterManifest.version }),
  check('release_status', releaseManifest.release_status === 'Temporary Technical Release', releaseManifest.release_status),
  check('owner_approval', releaseManifest.approval?.owner_visual === 'APPROVED', releaseManifest.approval),
  check('linguistic_status', releaseManifest.approval?.vietnamese_sign_language === 'NOT YET TESTED', releaseManifest.approval),
  check('static_manifest_hash', releaseManifest.assets?.static_preview_glb?.sha256 === staticAsset.sha256, releaseManifest.assets?.static_preview_glb),
  check('technical_manifest_hash', releaseManifest.assets?.technical_demo_glb?.sha256 === technicalAsset.sha256, releaseManifest.assets?.technical_demo_glb),
  check('master_manifest_consistency', masterManifest.exports?.static_preview_glb?.sha256 === staticAsset.sha256 && masterManifest.exports?.technical_demo_glb?.sha256 === technicalAsset.sha256, masterManifest.exports),
];

const report = {
  schema_version: 1,
  artifact: 'master_avatar_v1_release_validation',
  status: checks.every((item) => item.status === 'PASS') ? 'PASS' : 'FAIL',
  technical_validation: checks.every((item) => item.status === 'PASS') ? 'PASS' : 'FAIL',
  owner_visual_approval: 'APPROVED',
  linguistic_approval: 'NOT YET TESTED',
  static_asset: staticAsset,
  technical_asset: technicalAsset,
  checks,
};
mkdirSync(path.dirname(reportPath), { recursive: true });
writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
for (const item of checks) console.log(`${item.status} Master Avatar v1 GLB: ${item.id}`);
console.log(`${report.status} Master Avatar v1 release assets`);
if (report.status !== 'PASS') process.exitCode = 1;
