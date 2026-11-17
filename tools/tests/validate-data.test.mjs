import assert from 'node:assert/strict';
import { test } from 'node:test';
import { validateCanonicalData, validateSignsData } from '../validate-data.mjs';

const canonical = validateCanonicalData({ silent: true }).signs;

test('canonical sign metadata passes its schema and policy checks', () => {
  assert.deepEqual(validateSignsData(canonical), []);
});

test('duplicate sign IDs fail validation', () => {
  const duplicate = [...canonical, structuredClone(canonical[0])];
  assert.ok(validateSignsData(duplicate).some((error) => error.includes('duplicate sign id')));
});

test('unknown review status fails validation', () => {
  const invalid = structuredClone(canonical);
  invalid[0].reviewStatus = 'unknown';
  assert.ok(validateSignsData(invalid).some((error) => error.includes('must be equal to one of the allowed values')));
});

test('approved content requires genuine approval metadata', () => {
  const invalid = structuredClone(canonical);
  invalid[0].reviewStatus = 'approved';
  assert.ok(validateSignsData(invalid).length > 0);
});
