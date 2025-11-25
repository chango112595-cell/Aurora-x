import { NextRequest, NextResponse } from 'next/server'
import { getChatResponse } from '../../../server/aurora-chat'

export async function POST(request: NextRequest) {
  const { message, session_id } = await request.json()
  
  if (!message) {
    return NextResponse.json(
      { error: 'Message is required' },
      { status: 400 }
    )
  }
  
  const sessionId = session_id || 'default'
  const response = await getChatResponse(message, sessionId)
  
  return NextResponse.json({
    ok: true,
    response,
    message: response,
    session_id: sessionId,
    ai_powered: true
  })
}
