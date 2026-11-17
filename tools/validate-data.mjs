import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import Ajv2020 from 'ajv/dist/2020.js';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function readJson(relativePath) {
  return JSON.parse(readFileSync(path.join(projectRoot, relativePath), 'utf8'));
}

const ajv = new Ajv2020({ allErrors: true, strict: true });
const validateSignsSchema = ajv.compile(readJson('schemas/sign.schema.json'));
const validateQuizSchema = ajv.compile(readJson('schemas/quiz.schema.json'));

function formatAjvErrors(errors = []) {
  return errors.map((error) => `${error.instancePath || '/'} ${error.message}`);
}

export function validateSignsData(signs) {
  const errors = [];
  if (!validateSignsSchema(signs)) {
    errors.push(...formatAjvErrors(validateSignsSchema.errors));
  }

  if (Array.isArray(signs)) {
    const ids = new Set();
    for (const sign of signs) {
      if (ids.has(sign.id)) errors.push(`duplicate sign id: ${sign.id}`);
      ids.add(sign.id);
      if (sign.glbPath !== `models/signs/${sign.id}.glb`) {
        errors.push(`${sign.id}: glbPath must be models/signs/${sign.id}.glb`);
      }
      if (sign.animationClip !== `${sign.id}_MAIN`) {
        errors.push(`${sign.id}: animationClip must be ${sign.id}_MAIN`);
      }
    }
  }
  return errors;
}

export function validateQuizData(quizzes, knownSignIds) {
  const errors = [];
  if (!validateQuizSchema(quizzes)) {
    errors.push(...formatAjvErrors(validateQuizSchema.errors));
  }
  if (Array.isArray(quizzes)) {
    const ids = new Set();
    for (const quiz of quizzes) {
      if (ids.has(quiz.id)) errors.push(`duplicate quiz id: ${quiz.id}`);
      ids.add(quiz.id);
      if (!knownSignIds.has(quiz.signId)) errors.push(`${quiz.id}: unknown signId ${quiz.signId}`);
      if (!quiz.choices?.some((choice) => choice.id === quiz.correctChoiceId)) {
        errors.push(`${quiz.id}: correctChoiceId does not reference a choice`);
      }
    }
  }
  return errors;
}

export function validateCanonicalData({ silent = false } = {}) {
  const signs = readJson('data/signs.json');
  const quizzes = readJson('data/quizzes.json');
  const errors = [
    ...validateSignsData(signs).map((error) => `signs.json: ${error}`),
    ...validateQuizData(quizzes, new Set(signs.map((sign) => sign.id))).map((error) => `quizzes.json: ${error}`),
  ];
  if (!silent) {
    if (errors.length === 0) {
      console.log(`PASS data: ${signs.length} signs and ${quizzes.length} quizzes are valid.`);
    } else {
      for (const error of errors) console.error(`FAIL data: ${error}`);
    }
  }
  return { signs, quizzes, errors };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const { errors } = validateCanonicalData();
  process.exitCode = errors.length === 0 ? 0 : 1;
}
