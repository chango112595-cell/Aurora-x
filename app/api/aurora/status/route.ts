import { NextResponse } from 'next/server'
import { AuroraCore } from '../../../../server/aurora-core'

export async function GET() {
  const aurora = AuroraCore.getInstance()
  const status = aurora.getStatus()
  return NextResponse.json(status)
}
