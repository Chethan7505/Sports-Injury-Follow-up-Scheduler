import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { spawn } from 'node:child_process';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const backendDir = path.resolve(__dirname, '..');

function checkBackend() {
  return new Promise((resolve) => {
    const req = http.get('http://127.0.0.1:5000/api/config', (res) => {
      res.resume();
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(500, () => {
      req.destroy();
      resolve(false);
    });
  });
}

function autoFlaskBackend() {
  let flaskProc = null;

  const cleanup = () => {
    if (flaskProc && !flaskProc.killed) {
      flaskProc.kill('SIGTERM');
      flaskProc = null;
    }
  };

  return {
    name: 'auto-flask-backend',
    async configureServer(server) {
      if (await checkBackend()) return;

      const candidates = ['python3', '/opt/anaconda3/bin/python3', '/usr/bin/python3'];
      for (const py of candidates) {
        let exited = false;
        const proc = spawn(py, ['api.py'], {
          cwd: backendDir,
          env: { ...process.env, FLASK_NO_RELOADER: '1' },
          stdio: 'inherit',
        });
        proc.on('exit', () => { exited = true; });
        proc.on('error', () => { exited = true; });

        for (let i = 0; i < 30; i++) {
          if (exited) break;
          if (await checkBackend()) {
            flaskProc = proc;
            server.httpServer?.once('close', cleanup);
            process.once('exit', cleanup);
            return;
          }
          await new Promise((r) => setTimeout(r, 150));
        }

        if (!exited) proc.kill('SIGTERM');
      }
    },
  };
}

export default defineConfig({
  plugins: [react(), autoFlaskBackend()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://127.0.0.1:5000',
    },
  },
});
