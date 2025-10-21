import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.is_palindrome import is_palindrome


class Test_is_palindrome_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(is_palindrome(s='racecar'), True)
class Test_is_palindrome_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(is_palindrome(s='hello'), False)
class Test_is_palindrome_2(unittest.TestCase):
    def test_2(self):
        self.assertEqual(is_palindrome(s='a'), True)

if __name__=='__main__': unittest.main()
