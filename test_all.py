#!/usr/bin/env python3
"""
Test runner for all unit tests
"""

import unittest
import sys

# Import all test modules
from test_rule110 import (
    TestRule110,
    TestRule110Compiler,
    TestVisualize
)
from test_operations import (
    TestOperationCompiler,
    TestOperationExecutor,
    TestOperationLanguage
)


def create_test_suite():
    """Create and return a test suite with all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestRule110))
    suite.addTests(loader.loadTestsFromTestCase(TestRule110Compiler))
    suite.addTests(loader.loadTestsFromTestCase(TestVisualize))
    suite.addTests(loader.loadTestsFromTestCase(TestOperationCompiler))
    suite.addTests(loader.loadTestsFromTestCase(TestOperationExecutor))
    suite.addTests(loader.loadTestsFromTestCase(TestOperationLanguage))
    
    return suite


def run_tests():
    """Run all tests"""
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    run_tests()

