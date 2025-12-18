# Autonomous Agents Framework

Quickstart:
1. Create a Memory engine (see /memory)
2. Register tools:
   from agents.tools.shell_tool import shell_call
   tools = {"shell": Tool("shell", shell_call)}
3. Create agent:
   a = Agent("fixer", memory, tools, policy={"human_in_loop": True})
4. Schedule:
   from agents.agent_manager import AgentManager
   mgr = AgentManager(max_workers=2); mgr.start()
   mgr.submit(a, "Install package xyz")
5. Suggestions are saved under agents/suggestions for operator approval.

Security:
- Never set human_in_loop=False on production vehicle or aircraft agents
- Use container-backed tool adapters for untrusted code
