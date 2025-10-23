import unittest

from src.reverse_string import reverse_string


class T0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(reverse_string(s="hello"), "olleh")


class T1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(reverse_string(s="world"), "dlrow")


class T2(unittest.TestCase):
    def test_2(self):
        self.assertEqual(reverse_string(s="python"), "nohtyp")


if __name__ == "__main__":
    unittest.main()
