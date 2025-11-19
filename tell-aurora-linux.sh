#!/bin/bash
# Aurora Linux Installation - Tell Aurora about the system

echo "💬 Telling Aurora about Linux installation..."
echo ""

# Start Python interpreter and talk to Aurora
python3 << 'PYTHON_SCRIPT'
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from aurora_core import create_aurora_core
    
    print("🧠 Initializing Aurora Core...")
    aurora = create_aurora_core()
    
    message = """
    Aurora, I'm installing you on a Linux system. 
    
    Here's what you need to know:
    - Platform: Linux
    - Python: Python 3 (python3 command)
    - Virtual Environment: .venv/bin/activate (not .venv/Scripts/activate)
    - Path separator: / (not \\)
    - Services will run with systemd or tmux
    - The chat server needs to bind to 0.0.0.0 to be accessible
    - Port 5003 is the standard chat port
    
    The installation includes:
    - Flask chat server on port 5003
    - Frontend on port 5000
    - All Aurora services
    
    Please remember this for future Linux deployments.
    Can you confirm you understand the Linux environment?
    """
    
    # Process the message
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(
        aurora.process_conversation(message, "linux-installation")
    )
    loop.close()
    
    print("\n" + "="*60)
    print("🌟 Aurora's Response:")
    print("="*60)
    print(response)
    print("="*60)
    print("\n✅ Aurora has been informed about Linux installation!")
    
except Exception as e:
    print(f"⚠️  Could not communicate with Aurora: {e}")
    print("This is okay - Aurora will learn about the system as you use it.")

PYTHON_SCRIPT

echo ""
echo "✨ Setup complete! Aurora is aware of the Linux environment."
echo ""
echo "Next steps:"
echo "  ./start-aurora.sh   # Start all services"
echo "  python3 x-start     # Alternative start command"
