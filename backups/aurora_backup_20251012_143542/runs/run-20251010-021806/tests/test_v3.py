import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.add_two_numbers import add_two_numbers
class Test_add_two_numbers_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(add_two_numbers(a=1, b=2), 3)
class Test_add_two_numbers_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(add_two_numbers(a=-5, b=5), 0)

if __name__=='__main__': unittest.main()