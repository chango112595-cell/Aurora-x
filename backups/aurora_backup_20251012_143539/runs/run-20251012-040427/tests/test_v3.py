import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.create_test_function import create_test_function

if __name__=='__main__': unittest.main()