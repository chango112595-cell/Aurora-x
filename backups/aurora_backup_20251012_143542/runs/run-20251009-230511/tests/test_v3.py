import unittest
# SpecV3: Fibonacci
from src.fib import fib
class Test_fib_0(unittest.TestCase):
    def test_0(self):
        self.assertEqual(fib(n=0), 0)
class Test_fib_1(unittest.TestCase):
    def test_1(self):
        self.assertEqual(fib(n=1), 1)
class Test_fib_2(unittest.TestCase):
    def test_2(self):
        self.assertEqual(fib(n=5), 5)
class Test_fib_3(unittest.TestCase):
    def test_3(self):
        self.assertEqual(fib(n=10), 55)

if __name__=='__main__': unittest.main()