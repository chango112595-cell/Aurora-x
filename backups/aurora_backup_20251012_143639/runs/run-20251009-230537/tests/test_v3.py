import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
# SpecV3: Palindrome Checker
from src.reverse_string import reverse_string
from src.check_palindrome import check_palindrome
class Test_reverse_string_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(reverse_string(s='abc'), 'cba')
class Test_check_palindrome_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(check_palindrome(s='abba'), True)
class Test_check_palindrome_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(check_palindrome(s='abc'), False)

if __name__=='__main__': unittest.main()