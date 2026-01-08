import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const { message, session_id } = await request.json()

  if (!message) {
    return NextResponse.json(
      { error: 'Message is required' },
      { status: 400 }
    )
  }

  const sessionId = session_id || 'default'

  try {
    // Route to Luminar Nexus V2 for AI-powered responses
    const luminarResponse = await fetch('http://0.0.0.0:8000/api/nexus/ai/insights', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        context: 'chat_interface'
      })
    })

    if (!luminarResponse.ok) {
      throw new Error('Luminar Nexus V2 unavailable')
    }

    const data = await luminarResponse.json()

    // Learn from conversation pattern
    await fetch('http://0.0.0.0:8000/api/nexus/learn-conversation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        type: 'neural_chat',
        keywords: message.toLowerCase().split(' ').filter((w: string) => w.length > 3),
        confidence: 85,
        userMessage: message,
        context: sessionId
      })
    }).catch(() => {}) // Non-critical

    return NextResponse.json({
      ok: true,
      response: data.response || data.insight || 'Aurora is processing your request...',
      message: data.response || data.insight,
      session_id: sessionId,
      ai_powered: true,
      quantum_coherence: data.quantum_coherence || 1.0
    })
  } catch (error) {
    // Fallback to local processing
    const fallbackResponse = `Aurora AI analyzing: "${message}". Luminar Nexus V2 is initializing...`

    return NextResponse.json({
      ok: true,
      response: fallbackResponse,
      message: fallbackResponse,
      session_id: sessionId,
      ai_powered: false,
      fallback: true
    })
  }
}
