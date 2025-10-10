import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.reverse_string import reverse_string
class Test_reverse_string_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(reverse_string(s='abc'), 'cba')
class Test_reverse_string_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(reverse_string(s=''), '')
class Test_reverse_string_2(unittest.TestCase):
    def test_2(self):
        self.assertEqual(reverse_string(s='åß∂'), '∂ßå')

if __name__=='__main__': unittest.main()