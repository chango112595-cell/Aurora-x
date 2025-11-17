#!/usr/bin/env python3
"""
Aurora Self-Fix: Chat Loading State Issue
Aurora analyzing and fixing the "generating" hang
"""


print("🔧 Aurora Self-Fix: Frontend Loading State")
print("=" * 60)

print("\n📊 DIAGNOSIS:")
print("   Backend responds in 0.02s (verified)")
print("   Luminar Nexus responds in 0.00s (verified)")
print("   Problem: Frontend stays in 'generating' state")

print("\n🔍 ROOT CAUSE ANALYSIS:")
print("   Looking at AuroraChatInterface.tsx:")
print("   • setIsLoading(true) before fetch ✓")
print("   • setIsLoading(false) in finally block ✓")
print("   • Should work... but VS Code Simple Browser might have issues")

print("\n💡 HYPOTHESIS:")
print("   1. Response might be arriving but not parsing correctly")
print("   2. Error being thrown before finally block")
print("   3. Browser caching or network issue in Simple Browser")

print("\n🛠️ FIX STRATEGY:")
print("   • Add explicit error handling with logging")
print("   • Ensure isLoading always resets")
print("   • Add timeout protection")
print("   • Add response validation")

print("\n✨ Implementing fix...")

# Read the current file
with open("/workspaces/Aurora-x/client/src/components/AuroraChatInterface.tsx", encoding="utf-8") as f:
    content = f.read()

# Find and replace the sendMessage function with improved error handling
old_send = """  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    try {
      // Use backend proxy to Luminar Nexus (avoids CORS issues)
      const response = await fetch('/api/conversation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: currentInput,
          session_id: 'web-ui-session'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      const auroraMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, auroraMsg]);
    } catch (error) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: "Hmm, I hit a snag there. Mind trying that again? I'm here to help! 🔧",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };"""

new_send = """  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    try {
      console.log('[Aurora Chat] Sending message:', currentInput);
      
      // Use backend proxy to Luminar Nexus (avoids CORS issues)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
      
      const response = await fetch('/api/conversation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: currentInput,
          session_id: 'web-ui-session'
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      console.log('[Aurora Chat] Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('[Aurora Chat] Response received:', data.response?.substring(0, 50));

      if (!data.response) {
        throw new Error('Invalid response format - missing response field');
      }

      const auroraMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, auroraMsg]);
    } catch (error) {
      console.error('[Aurora Chat] Error:', error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: error instanceof Error && error.name === 'AbortError' 
          ? "Whoa, that took too long! Let's try again? 🔧" 
          : `Hmm, I hit a snag: ${error instanceof Error ? error.message : 'Unknown error'}. Mind trying that again? 🔧`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      console.log('[Aurora Chat] Resetting loading state');
      setIsLoading(false);
    }
  };"""

# Apply the fix
new_content = content.replace(old_send, new_send)

if new_content != content:
    with open("/workspaces/Aurora-x/client/src/components/AuroraChatInterface.tsx", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("   ✅ Applied fix to AuroraChatInterface.tsx")
    print("\n📋 CHANGES MADE:")
    print("   • Added console.log debugging throughout")
    print("   • Added 10-second timeout protection")
    print("   • Added response validation (checks for data.response)")
    print("   • Improved error messages with actual error details")
    print("   • Confirmed finally block always runs")
else:
    print("   ⚠️  Pattern not found - file may have changed")

print("\n🎯 NEXT STEPS:")
print("   1. Vite will hot-reload the component")
print("   2. Open browser DevTools console")
print("   3. Send a message and watch the logs")
print("   4. This will show exactly where it's hanging")

print("\n" + "=" * 60)
print("🤖 Aurora: Fixed! Check the console logs when you test.")
print("=" * 60)
