import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import { resolve } from 'path';
import { getPythonPath } from '@/lib/get_python_path';

export async function POST(request: Request) {
  try {
    const { question } = await request.json();

    if (!question || typeof question !== 'string') {
      return NextResponse.json(
        { error: 'Invalid question format' },
        { status: 400 }
      );
    }

    // Get Python path from venv
    const pythonPath = getPythonPath();

    // Path to Python script relative to api route
    const pythonScriptPath = resolve(process.cwd(), 'src/lib/shoe_advisor.py');
    
    console.log('Using Python from:', pythonPath);
    console.log('Running script:', pythonScriptPath);
    console.log('Question:', question);

    // Spawn Python process
    const pythonProcess = spawn(pythonPath, [pythonScriptPath, question], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    return new Promise((resolve, reject) => {
      let stdoutData = '';
      let stderrData = '';

      pythonProcess.stdout.on('data', (data) => {
        stdoutData += data.toString();
        console.log('Python stdout:', data.toString());
      });

      pythonProcess.stderr.on('data', (data) => {
        stderrData += data.toString();
        console.error('Python stderr:', data.toString());
      });

      pythonProcess.on('error', (err) => {
        console.error('Process error:', err);
        reject(new Error(`Failed to start Python process: ${err.message}`));
      });

      pythonProcess.on('close', (code) => {
        console.log('Python process closed with code:', code);
        console.log('Final stdout:', stdoutData);
        console.log('Final stderr:', stderrData);

        if (code !== 0) {
          return reject(new Error(`Python process exited with code ${code}: ${stderrData}`));
        }

        // Try to find valid JSON in the output
        try {
          const trimmedOutput = stdoutData.trim();
          if (!trimmedOutput) {
            throw new Error('No output from Python script');
          }

          const parsedResult = JSON.parse(trimmedOutput);
          resolve(NextResponse.json(parsedResult));
        } catch (e) {
          console.error('Parse error:', e);
          console.error('Raw stdout:', stdoutData);
          console.error('Raw stderr:', stderrData);
          reject(new Error('Failed to parse Python output. Check server logs for details.'));
        }
      });
    });
  } catch (error) {
    console.error('Request error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to process request', 
        details: error instanceof Error ? error.message : 'Unknown error',
        type: error.constructor.name
      },
      { status: 500 }
    );
  }
}