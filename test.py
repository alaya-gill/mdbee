import unittest

class Fibonacci:
    
    def calculate(self, arg):
        
        if arg < 2:
            return arg
        num = 0
        fib_series = [0, 1]
        for i in range(1,arg+1):
            num += fib_series[i-1] + fib_series[i-2]
            fib_series += [num]
        return num
    
# fibonacci = Fibonacci()
# print(fibonacci.calculate(5))
            
class TestFibonacci(unittest.TestCase):
    
    def test_fibonacci_0_should_be(self):
        fibonacci = Fibonacci()
        self.assertEqual(0, fibonacci.calculate(0))
        
