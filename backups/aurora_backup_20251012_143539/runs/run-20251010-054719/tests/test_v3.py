import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.count_vowels import count_vowels


class Test_count_vowels_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(count_vowels(s='hello'), 2)
class Test_count_vowels_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(count_vowels(s='xyz'), 0)
class Test_count_vowels_2(unittest.TestCase):
    def test_2(self):
        self.assertEqual(count_vowels(s='aeiou'), 5)

if __name__=='__main__': unittest.main()
