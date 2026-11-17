import js from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  {
    ignores: ['**/dist/**', '**/node_modules/**', 'apps/web/public/data/**'],
  },
  {
    files: ['apps/web/src/**/*.{ts,tsx}', 'apps/web/tests/**/*.{ts,tsx}'],
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    languageOptions: {
      globals: {
        document: 'readonly',
        localStorage: 'readonly',
        window: 'readonly',
      },
    },
  },
);
