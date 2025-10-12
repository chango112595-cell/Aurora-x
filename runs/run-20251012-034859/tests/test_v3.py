import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.generate_hello_world_function import generate_hello_world_function

if __name__=='__main__': unittest.main()