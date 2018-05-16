"""
runs basic tests
"""
import unittest
import sys
sys.path.append("..")  # Adds higher directory to python modules path.
import fuzzix


class FuzzixTest(unittest.TestCase):
    """tests the functions owned by the fuzzix module"""

    def test_print_banner(self):
        """
        tests the print_banner function
        return: None
        """
        try:
            fuzzix.print_banner()
        except:
            self.fail('print_banner() raised an exception')


if __name__ == '__main__':
    unittest.main()
