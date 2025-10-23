import unittest

from src.add_two_numbers import add_two_numbers


class T0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(add_two_numbers(a=2, b=3), 5)


class T1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(add_two_numbers(a=10, b=20), 30)


class T2(unittest.TestCase):
    def test_2(self):
        self.assertEqual(add_two_numbers(a=-5, b=5), 0)


if __name__ == "__main__":
    unittest.main()
