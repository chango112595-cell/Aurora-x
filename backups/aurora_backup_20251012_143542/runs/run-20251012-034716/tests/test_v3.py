import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.write_simple_hello_world import write_simple_hello_world

if __name__=='__main__': unittest.main()