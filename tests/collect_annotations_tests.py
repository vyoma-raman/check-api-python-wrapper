import unittest
import sys
import os
import warnings
from expected_response import xr_nodes, xr_pivot1, xr_pivot2
sys.path.append('../check_api')
from meedan_interface import MeedanAPI
import util

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.key = os.environ.get('MEEDAN_KEY')
        self.meedan_api = MeedanAPI(self.key, "ischool-hrc")
        warnings.simplefilter("ignore", ResourceWarning)

    def test(self):
        response = self.meedan_api.collect_annotations()
        print(response["I_izvAbhExY"])

if __name__ == '__main__':
    unittest.main()
