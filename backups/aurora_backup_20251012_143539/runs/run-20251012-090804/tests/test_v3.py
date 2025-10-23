import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.fibonacci import fibonacci


class Test_fibonacci_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(fibonacci(n=0), 0)


class Test_fibonacci_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(fibonacci(n=1), 1)


class Test_fibonacci_2(unittest.TestCase):
    def test_2(self):
        self.assertEqual(fibonacci(n=6), 8)


if __name__ == "__main__":
    unittest.main()
