import assert from 'node:assert/strict';
import test from 'node:test';
import { validateMotionSpecFile, validateMotionSpec } from '../validate-sign-motion-spec.mjs';

test('technical pose-authoring pilot validates', () => {
  const result = validateMotionSpecFile();
  assert.deepEqual(result.errors, []);
});

test('unknown pose is rejected', () => {
  const { spec, poseLibrary } = validateMotionSpecFile();
  const copy = structuredClone(spec);
  copy.key_poses[1].left_hand.pose = 'invented_pose';
  assert.ok(validateMotionSpec(copy, poseLibrary).some((error) => error.includes('unknown pose')));
});

test('technical fixture cannot claim a sign id', () => {
  const { spec, poseLibrary } = validateMotionSpecFile();
  const copy = structuredClone(spec);
  copy.identification.sign_id = 'S001';
  assert.ok(validateMotionSpec(copy, poseLibrary).length > 0);
});
