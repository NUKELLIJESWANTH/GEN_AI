import { spawn } from 'child_process';

// Ignore all arguments (like --port or --host) appended by the control plane
const child = spawn('streamlit', [
  'run',
  'app.py',
  '--server.port', '3000',
  '--server.address', '0.0.0.0',
  '--server.headless', 'true',
  '--server.enableCORS', 'false',
  '--server.enableXsrfProtection', 'false',
  '--browser.gatherUsageStats', 'false'
], {
  stdio: 'inherit'
});

child.on('exit', (code) => {
  process.exit(code || 0);
});
