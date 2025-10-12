import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.generate_random_haiku_about import generate_random_haiku_about

if __name__=='__main__': unittest.main()