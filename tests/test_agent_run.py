#!/usr/bin/env python3
from agents.agent_core import Agent
from agents.tools.shell_tool import shell_call
from memory.vecstore import MemoryStore
from agents.agent_manager import AgentManager

def test_basic():
    mem = MemoryStore()
    mem.write("alice is a programmer")
    tools = {"shell": type("T",(object,),{"name":"shell","call":shell_call})()}
    agent = Agent("test", mem, {"shell": tools["shell"]}, policy={"human_in_loop": True})
    res = agent.run("install testpkg")
    print("run results", res)

if __name__ == "__main__":
    test_basic()
