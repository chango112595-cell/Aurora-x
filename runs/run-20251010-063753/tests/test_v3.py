import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.sort_list import sort_list


class Test_sort_list_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(sort_list(nums="[3, 1, 2]"), "[1, 2, 3]")


class Test_sort_list_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(sort_list(nums="[5, -1, 0]"), "[-1, 0, 5]")


if __name__ == "__main__":
    unittest.main()
