"""Tests for test"""
import sys
sys.path.insert(0, "..")
from test import *

# Run the main function to execute built-in tests
if __name__ == "__main__":
    import subprocess
    subprocess.run([sys.executable, f"../test.py"])
