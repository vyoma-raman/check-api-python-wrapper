import unittest
import sys
import os
import warnings
from expected_response import xr_dbid_id, xr_list_names, xr_medias_count,xr_descriptions
sys.path.append('..')
from check_api.meedan_interface import MeedanAPI

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.key = os.environ.get('MEEDAN_KEY')
        self.meedan_api = MeedanAPI(self.key)
        warnings.simplefilter("ignore", ResourceWarning)

    #TODO: Finish fleshing out test once add_video is implemented
    def test_add(self):
        response = self.meedan_api.add_video("C2xel6q0yao", "#Wietske")

if __name__ == '__main__':
    unittest.main()
