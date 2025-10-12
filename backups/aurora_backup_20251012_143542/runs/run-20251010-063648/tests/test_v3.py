import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.sum_of_squares import sum_of_squares
class Test_sum_of_squares_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(sum_of_squares(nums='[1, 2, 3]'), 14)
class Test_sum_of_squares_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(sum_of_squares(nums='[0, 4, 5]'), 41)

if __name__=='__main__': unittest.main()