#!/usr/bin/env python3
"""
Test suite for Rule 110 Compiler

Verifies that all gates and arithmetic operations work correctly.
"""

import unittest
from gates import IdentityGate, NotGate, OrGate, AndGate, XorGate
from adder import HalfAdder, FullAdder, RippleCarryAdder


class TestGates(unittest.TestCase):
    """Test individual logic gates"""
    
    def test_identity(self):
        gate = IdentityGate()
        self.assertEqual(gate.compute(0), 0)
        self.assertEqual(gate.compute(1), 1)
    
    def test_not(self):
        gate = NotGate()
        self.assertEqual(gate.compute(0), 1)
        self.assertEqual(gate.compute(1), 0)
    
    def test_or(self):
        gate = OrGate()
        self.assertEqual(gate.compute(0, 0), 0)
        self.assertEqual(gate.compute(0, 1), 1)
        self.assertEqual(gate.compute(1, 0), 1)
        self.assertEqual(gate.compute(1, 1), 1)
    
    def test_and(self):
        gate = AndGate()
        self.assertEqual(gate.compute(0, 0), 0)
        self.assertEqual(gate.compute(0, 1), 0)
        self.assertEqual(gate.compute(1, 0), 0)
        self.assertEqual(gate.compute(1, 1), 1)
    
    def test_xor(self):
        gate = XorGate()
        self.assertEqual(gate.compute(0, 0), 0)
        self.assertEqual(gate.compute(0, 1), 1)
        self.assertEqual(gate.compute(1, 0), 1)
        self.assertEqual(gate.compute(1, 1), 0)


class TestHalfAdder(unittest.TestCase):
    """Test half-adder"""
    
    def setUp(self):
        self.ha = HalfAdder()
    
    def test_0_plus_0(self):
        s, c = self.ha.compute(0, 0)
        self.assertEqual((s, c), (0, 0))
    
    def test_0_plus_1(self):
        s, c = self.ha.compute(0, 1)
        self.assertEqual((s, c), (1, 0))
    
    def test_1_plus_0(self):
        s, c = self.ha.compute(1, 0)
        self.assertEqual((s, c), (1, 0))
    
    def test_1_plus_1(self):
        s, c = self.ha.compute(1, 1)
        self.assertEqual((s, c), (0, 1))


class TestFullAdder(unittest.TestCase):
    """Test full-adder"""
    
    def setUp(self):
        self.fa = FullAdder()
    
    def test_all_combinations(self):
        truth_table = [
            ((0, 0, 0), (0, 0)),
            ((0, 0, 1), (1, 0)),
            ((0, 1, 0), (1, 0)),
            ((0, 1, 1), (0, 1)),
            ((1, 0, 0), (1, 0)),
            ((1, 0, 1), (0, 1)),
            ((1, 1, 0), (0, 1)),
            ((1, 1, 1), (1, 1)),
        ]
        for (a, b, cin), (expected_sum, expected_cout) in truth_table:
            with self.subTest(a=a, b=b, cin=cin):
                s, c = self.fa.compute(a, b, cin)
                self.assertEqual((s, c), (expected_sum, expected_cout))


class TestRippleCarryAdder(unittest.TestCase):
    """Test multi-bit adder"""
    
    def setUp(self):
        self.adder = RippleCarryAdder(bits=8)
    
    def test_zero_plus_zero(self):
        self.assertEqual(self.adder.compute(0, 0), 0)
    
    def test_one_plus_one(self):
        self.assertEqual(self.adder.compute(1, 1), 2)
    
    def test_15_plus_31(self):
        """The original test case!"""
        self.assertEqual(self.adder.compute(15, 31), 46)
    
    def test_255_plus_1(self):
        """Overflow case"""
        self.assertEqual(self.adder.compute(255, 1), 256)
    
    def test_arbitrary_additions(self):
        test_cases = [
            (0, 0, 0),
            (1, 0, 1),
            (0, 1, 1),
            (7, 8, 15),
            (15, 16, 31),
            (100, 55, 155),
            (127, 128, 255),
        ]
        for a, b, expected in test_cases:
            with self.subTest(a=a, b=b):
                self.assertEqual(self.adder.compute(a, b), expected)


class TestFourBitAdder(unittest.TestCase):
    """Test 4-bit adder specifically"""
    
    def setUp(self):
        self.adder = RippleCarryAdder(bits=4)
    
    def test_all_single_digit(self):
        for a in range(10):
            for b in range(10 - a):
                with self.subTest(a=a, b=b):
                    self.assertEqual(self.adder.compute(a, b), a + b)


if __name__ == '__main__':
    unittest.main(verbosity=2)

