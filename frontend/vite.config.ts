import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig } from 'vite';

const BACKEND_PORT = process.env.BACKEND_PORT || '8679';

export default defineConfig(() => {
  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      port: 3000,
      host: true,
      hmr: process.env.DISABLE_HMR !== 'true',
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
      // Proxy API calls to the FastAPI backend so the frontend works with a
      // same-origin base URL during development (no CORS headaches).
      proxy: {
        '/api': {
          target: `http://localhost:${BACKEND_PORT}`,
          changeOrigin: true,
          // SSE support
          configure: (proxyServer) => {
            proxyServer.on('proxyReq', (proxyReq) => {
              proxyReq.setHeader('X-Accel-Buffering', 'no');
            });
          },
        },
      },
    },
  };
});
