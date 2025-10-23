import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.max_in_list import max_in_list


class Test_max_in_list_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(max_in_list(nums="[1, 2, 3]"), 3)


class Test_max_in_list_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(max_in_list(nums="[-5, 10, 0]"), 10)


if __name__ == "__main__":
    unittest.main()
