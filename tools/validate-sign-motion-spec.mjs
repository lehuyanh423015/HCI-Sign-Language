import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import Ajv2020 from 'ajv/dist/2020.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argument = (name, fallback) => {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
};
const readJson = (filePath) => JSON.parse(readFileSync(filePath, 'utf8'));
const schemaPath = path.resolve(root, argument('--schema', 'docs/contracts/sign-motion-spec.schema.json'));
const defaultSpecPath = path.resolve(root, argument('--spec', 'blender/animation-specs/TECH_POSE_AUTHORING_PILOT.json'));
const defaultPoseLibraryPath = path.resolve(root, argument('--pose-library', 'blender/poses/technical-hand-poses.json'));

const ajv = new Ajv2020({ allErrors: true, strict: true });
const validateSchema = ajv.compile(readJson(schemaPath));

export function validateMotionSpec(spec, poseLibrary) {
  const errors = [];
  if (!validateSchema(spec)) {
    errors.push(...(validateSchema.errors ?? []).map((error) => `${error.instancePath || '/'} ${error.message}`));
  }
  if (spec && Array.isArray(spec.key_poses)) {
    const frames = spec.key_poses.map((pose) => pose.frame);
    if (new Set(frames).size !== frames.length) errors.push('key_poses frame values must be unique');
    if (frames.some((frame, index) => index > 0 && frame <= frames[index - 1])) errors.push('key_poses must be strictly increasing by frame');
    if (spec.timing && frames.some((frame) => frame > spec.timing.duration_frames)) errors.push('key pose exceeds duration_frames');
    const knownPoses = new Set(Object.keys(poseLibrary?.poses ?? {}));
    for (const keyPose of spec.key_poses) {
      for (const side of ['left_hand', 'right_hand']) {
        if (!knownPoses.has(keyPose[side]?.pose)) errors.push(`${keyPose.label}: unknown pose ${keyPose[side]?.pose}`);
      }
    }
  }
  if (spec?.classification === 'TECHNICAL_FIXTURE_NOT_A_SIGN') {
    if (spec.identification?.sign_id !== null) errors.push('technical fixture must not use a sign_id');
    if (spec.review?.linguistic_status !== 'NOT_APPLICABLE') errors.push('technical fixture linguistic_status must be NOT_APPLICABLE');
  }
  return errors;
}

export function validateMotionSpecFile(specPath = defaultSpecPath, poseLibraryPath = defaultPoseLibraryPath) {
  const spec = readJson(specPath);
  const poseLibrary = readJson(poseLibraryPath);
  const errors = validateMotionSpec(spec, poseLibrary);
  return { spec, poseLibrary, errors };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const { spec, poseLibrary, errors } = validateMotionSpecFile();
  const reportPathArgument = argument('--report', '');
  const report = {
    schema_version: 1,
    artifact: 'sign_motion_spec_validation',
    status: errors.length === 0 ? 'PASS' : 'FAIL',
    classification: spec.classification,
    fixture_id: spec.identification?.fixture_id ?? null,
    sign_id: spec.identification?.sign_id ?? null,
    animation_name: spec.identification?.animation_name ?? null,
    duration_frames: spec.timing?.duration_frames ?? null,
    key_pose_count: spec.key_poses?.length ?? 0,
    pose_library_entries: Object.keys(poseLibrary.poses ?? {}).sort(),
    errors,
  };
  if (reportPathArgument) {
    const reportPath = path.resolve(root, reportPathArgument);
    mkdirSync(path.dirname(reportPath), { recursive: true });
    writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  }
  console.log(`${report.status} motion spec: ${report.animation_name} (${report.key_pose_count} poses, ${report.duration_frames} frames)`);
  for (const error of errors) console.error(`FAIL motion spec: ${error}`);
  if (errors.length) process.exitCode = 1;
}
