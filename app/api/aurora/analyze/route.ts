import { NextRequest, NextResponse } from 'next/server'
import { AuroraCore } from '../../../../server/aurora-core'

export async function POST(request: NextRequest) {
  const { input, context } = await request.json()
  const aurora = AuroraCore.getInstance()
  const result = await aurora.analyze(input, context)
  return NextResponse.json(result)
}
