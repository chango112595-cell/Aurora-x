import unittest

from src.reverse_string import reverse_string


class T0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(reverse_string(s='"abc"'), '"cba"')


class T1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(reverse_string(s='""'), '""')


class T2(unittest.TestCase):
    def test_2(self):
        self.assertEqual(reverse_string(s='"åß∂"'), '"∂ßå"')


if __name__ == "__main__":
    unittest.main()
