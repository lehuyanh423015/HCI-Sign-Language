import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { validateCanonicalData } from './validate-data.mjs';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const destinationDirectory = path.join(projectRoot, 'apps', 'web', 'public', 'data');
const files = ['signs.json', 'quizzes.json'];
const checkOnly = process.argv.includes('--check');
const { errors } = validateCanonicalData({ silent: true });

if (errors.length > 0) {
  for (const error of errors) console.error(`FAIL sync: ${error}`);
  process.exitCode = 1;
} else if (checkOnly) {
  const stale = files.filter((file) => {
    try {
      return readFileSync(path.join(projectRoot, 'data', file), 'utf8') !== readFileSync(path.join(destinationDirectory, file), 'utf8');
    } catch {
      return true;
    }
  });
  if (stale.length > 0) {
    console.error(`FAIL sync: generated web data is missing or stale: ${stale.join(', ')}`);
    process.exitCode = 1;
  } else {
    console.log('PASS sync: web data matches canonical data/.');
  }
} else {
  mkdirSync(destinationDirectory, { recursive: true });
  for (const file of files) {
    copyFileSync(path.join(projectRoot, 'data', file), path.join(destinationDirectory, file));
  }
  console.log(`PASS sync: copied ${files.length} validated files to apps/web/public/data/.`);
}
