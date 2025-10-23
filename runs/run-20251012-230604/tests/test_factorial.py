import unittest

from src.factorial import factorial


class T0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(factorial(n=0), 1)


class T1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(factorial(n=5), 120)


class T2(unittest.TestCase):
    def test_2(self):
        self.assertEqual(factorial(n=3), 6)


if __name__ == "__main__":
    unittest.main()
