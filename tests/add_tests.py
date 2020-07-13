import unittest
import sys
import os
import warnings
sys.path.append('..')
from check_api.meedan_interface import MeedanAPI

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.key = os.environ.get('MEEDAN_KEY')
        self.meedan_api = MeedanAPI(self.key)
        warnings.simplefilter("ignore", ResourceWarning)

    #TODO: Finish fleshing out tests once method is completed
    def test_add(self):
        response = self.meedan_api.add_video("C2xel6q0yao", "#Wietske")

if __name__ == '__main__':
    unittest.main()
