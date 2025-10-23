import unittest

from src.add_two_numbers import add_two_numbers


class TestAdd(unittest.TestCase):
    def test_pos(self):
        self.assertEqual(add_two_numbers(1, 2), 3)

    def test_neg(self):
        self.assertEqual(add_two_numbers(-5, 5), 0)

    def test_zero(self):
        self.assertEqual(add_two_numbers(0, 0), 0)


if __name__ == "__main__":
    unittest.main()
