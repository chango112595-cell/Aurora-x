/**
 * Health Check API Route - Next.js App Router
 */
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'Aurora Next.js 16',
    version: '2.0.0',
  });
}
