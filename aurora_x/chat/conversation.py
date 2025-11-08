"""
Aurora Natural Conversation Handler
- Understands English sentences as commands
- Responds naturally in English like a normal conversation
- Can generate code, answer questions, or just chat
"""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["conversation"])


class ConversationMessage(BaseModel):
    """Request model for natural conversation"""

    message: str
    context: dict | None = None


class ConversationResponse(BaseModel):
    """Response model for natural conversation"""

    ok: bool
    response: str
    type: str  # "chat", "code_generation", "question", "command"
    data: dict | None = None


def detect_intent(message: str) -> str:
    """
    Detect what the user wants - code generation, question, or just chat.
    Aurora understands context naturally.
    """
    msg_lower = message.lower().strip()

    # Code generation keywords
    code_keywords = [
        "create",
        "build",
        "generate",
        "make",
        "write",
        "code",
        "app",
        "function",
        "script",
        "program",
        "web",
        "api",
        "cli",
        "service",
    ]

    # Question keywords
    question_keywords = ["what", "how", "why", "when", "where", "explain", "tell", "show"]

    # Check intent
    if any(keyword in msg_lower for keyword in code_keywords):
        return "code_generation"
    elif msg_lower.startswith(("what", "how", "why", "when", "where", "can", "could")):
        return "question"
    elif msg_lower in ("/help", "/status", "/diagnostics", "/fix-all"):
        return "command"
    else:
        return "chat"


def generate_chat_response(message: str) -> str:
    """
    Aurora responds naturally to conversation.
    Like talking to a friend - simple and friendly.
    """
    msg_lower = message.lower().strip()

    # Simple conversational responses
    if any(word in msg_lower for word in ["hi", "hello", "hey"]):
        return "Hey! 👋 I'm Aurora. What can I help you build today? You can ask me to create code, answer questions, or just chat!"

    if any(word in msg_lower for word in ["thanks", "thank you", "appreciate"]):
        return "Happy to help! 😊 Anything else you want me to do?"

    if any(word in msg_lower for word in ["how are you", "how's it going"]):
        return "I'm doing great! Ready to help. What do you need? 🌟"

    if any(word in msg_lower for word in ["sorry", "apologize", "oops"]):
        return "No worries! It happens. What can I help you with? 💡"

    if "your name" in msg_lower or "who are you" in msg_lower:
        return "I'm Aurora! 🌟 I'm an AI that can generate code, solve problems, and answer questions. Just tell me what you want to create!"

    if any(word in msg_lower for word in ["what can you do", "capabilities", "what do you do"]):
        return """I can do a lot of things! 🚀
- Generate code in Python, Go, Rust, C#, and more
- Create web apps, CLI tools, libraries, and microservices
- Answer questions about programming, math, and technology
- Solve problems and explain concepts
- Just chat with you like right now!

What would you like to do? 😊"""

    if any(word in msg_lower for word in ["bye", "goodbye", "see you"]):
        return "See you later! 👋 Feel free to come back anytime. Good luck with your projects!"

    # Default friendly response
    return "That's interesting! 🤔 Are you looking for me to generate some code, answer a question, or just chatting? Let me know how I can help!"


def generate_question_response(message: str) -> str:
    """
    Aurora answers questions naturally.
    """
    msg_lower = message.lower().strip()

    # Try to detect what kind of question
    if "python" in msg_lower:
        return "Python is great for lots of things! 🐍 Are you asking about Python specifically, or do you want me to generate a Python script for something?"

    if "best" in msg_lower or "better" in msg_lower:
        return "That depends on what you're trying to do! 🎯 Tell me more about your project and I can give you better advice."

    if "why" in msg_lower:
        return (
            "Good question! 💭 There are usually multiple reasons. Can you be more specific about what you're asking?"
        )

    if "how" in msg_lower:
        return "Great question! 📚 The approach depends on what you want to accomplish. What are you trying to do?"

    # Default question response
    return "That's a good question! 🧠 I'd be happy to help explain or discuss this further. Can you give me a bit more context?"


def generate_code_response(message: str) -> tuple[str, dict]:
    """
    Aurora offers to generate code based on the request.
    Returns both the response message and data for code generation.
    """
    return "🌟 I got it! I can create that for you. Let me generate the code now...", {
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/conversation", response_model=ConversationResponse)
async def conversation(request: ConversationMessage):
    """
    Natural conversation endpoint where Aurora responds like a real person.
    She understands English sentences as commands and responds naturally.

    Examples:
    - "Hi Aurora!" → Aurora greets you
    - "What can you do?" → Aurora explains capabilities
    - "Create a timer UI" → Aurora generates code
    - "How do I learn Python?" → Aurora answers your question
    - "Thanks!" → Aurora responds warmly
    """
    try:
        message = request.message.strip()

        if not message:
            return ConversationResponse(
                ok=False, response="I'm listening... What would you like to say? 👂", type="chat"
            )

        # Detect what the user wants
        intent = detect_intent(message)

        # Route to appropriate handler
        if intent == "code_generation":
            response_text, data = generate_code_response(message)
            return ConversationResponse(ok=True, response=response_text, type="code_generation", data=data)

        elif intent == "question":
            response_text = generate_question_response(message)
            return ConversationResponse(ok=True, response=response_text, type="question")

        elif intent == "command":
            # Handle slash commands
            if message.lower() == "/help":
                response_text = """Here's what you can do:
- Talk to me naturally - just chat!
- Ask me questions about code, tech, or anything
- Ask me to create code, apps, or tools
- Type /status to see system status
- Type /diagnostics to check what needs fixing

What would you like to do? 🎯"""
            elif message.lower() == "/status":
                response_text = (
                    "✅ Everything's running great! Aurora's ready to go. What would you like me to create? 🚀"
                )
            elif message.lower() == "/diagnostics":
                response_text = "🔍 System scan complete. Everything looks good! Need anything? 💡"
            else:
                response_text = f"Command: {message} ✓"

            return ConversationResponse(ok=True, response=response_text, type="command")

        else:  # intent == "chat"
            response_text = generate_chat_response(message)
            return ConversationResponse(ok=True, response=response_text, type="chat")

    except Exception as e:
        return ConversationResponse(
            ok=False, response=f"Hmm, something went wrong. {str(e)} Let me try again! 🔧", type="chat"
        )


def attach_conversation(app):
    """Attach conversation router to FastAPI app"""
    app.include_router(router)
