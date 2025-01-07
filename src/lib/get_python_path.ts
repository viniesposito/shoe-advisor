import { resolve } from 'path';
import { existsSync } from 'fs';

export function getPythonPath(): string {
//   const isDev = process.env.NODE_ENV === 'development';
  const rootDir = process.cwd();

  // Check for virtual environment
  const venvPython = process.platform === 'win32'
    ? resolve(rootDir, '.venv', 'Scripts', 'python.exe')
    : resolve(rootDir, '.venv', 'bin', 'python');

  if (existsSync(venvPython)) {
    return venvPython;
  }

  throw new Error('Virtual environment Python not found. Please run: uv venv && source .venv/bin/activate && uv pip install -r requirements.txt');
}