import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { createApi } from '../server/api.mjs';

function accounts(): Plugin {
  return {
    name: 'hci-accounts',
    configureServer(server) { server.middlewares.use(createApi()); },
    configurePreviewServer(server) { server.middlewares.use(createApi()); },
  };
}

export default defineConfig({
  plugins: [react(), tailwindcss(), accounts()],
  server: { fs: { deny: ['.env', '.env.*', '*.{crt,pem}', '**/.git/**', '**/.hci-private/**', '**/*.sqlite*', '**/apps/server/**', '**/data/quizzes.json', '**/data/signs.json'] } },
});
