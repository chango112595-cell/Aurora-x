"""Tests for hello_world"""
import sys

sys.path.insert(0, "..")
from hello_world import *

# Run the main function to execute built-in tests
if __name__ == "__main__":
    import subprocess
    subprocess.run([sys.executable, "../hello_world.py"])
