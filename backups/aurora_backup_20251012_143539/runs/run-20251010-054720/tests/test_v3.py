import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.gcd import gcd


class Test_gcd_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(gcd(a=12, b=8), 4)
class Test_gcd_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(gcd(a=17, b=5), 1)

if __name__=='__main__': unittest.main()
