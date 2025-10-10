import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.is_prime import is_prime
class Test_is_prime_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(is_prime(n=2), True)
class Test_is_prime_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(is_prime(n=17), True)
class Test_is_prime_2(unittest.TestCase):
    def test_2(self):
        self.assertEqual(is_prime(n=4), False)

if __name__=='__main__': unittest.main()