import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.factorial import factorial


class Test_factorial_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(factorial(n=0), 1)


class Test_factorial_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(factorial(n=5), 120)


class Test_factorial_2(unittest.TestCase):
    def test_2(self):
        self.assertEqual(factorial(n=3), 6)


if __name__ == "__main__":
    unittest.main()
