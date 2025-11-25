/**
 * Aurora Error Reporting API Route
 * Receives and logs runtime errors from client
 */
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function POST(request: Request) {
  try {
    const errorData = await request.json();

    // Log to console
    console.error('[AURORA ERROR REPORT]', errorData);

    // Save to error log file
    const logDir = path.join(process.cwd(), 'logs');
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }

    const logFile = path.join(logDir, 'aurora-errors.log');
    const logEntry = `
${new Date().toISOString()} - ${errorData.type}
Message: ${errorData.message}
${errorData.location ? `Location: ${errorData.location.file}:${errorData.location.line}:${errorData.location.column}` : ''}
${errorData.stack ? `Stack: ${errorData.stack}` : ''}
${'='.repeat(80)}
`;

    fs.appendFileSync(logFile, logEntry);

    // TODO: Trigger Aurora's autonomous fix system
    // Aurora should analyze the error and attempt to fix it

    return NextResponse.json({ 
      success: true, 
      message: 'Error reported to Aurora',
    });
  } catch (error) {
    console.error('[AURORA] Failed to process error report:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to process error report' },
      { status: 500 }
    );
  }
}
