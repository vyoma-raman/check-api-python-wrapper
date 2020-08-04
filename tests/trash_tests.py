import unittest
import sys
import os
import warnings
sys.path.append('../check_api')
from meedan_interface import MeedanAPI

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.key = os.environ.get('MEEDAN_KEY')
        self.meedan_api = MeedanAPI(self.key, "ischool-hrc")
        warnings.simplefilter("ignore", ResourceWarning)

    #TODO: Finish fleshing out tests once method is completed
    def test_trash(self):
        response = self.meedan_api.trash_video("UHJvamVjdE1lZGlhLzM5MzY5Mg==\n")
        self.assertTrue(response)

    def test_trash_list(self):
        response = self.meedan_api.trash_video_list(["UHJvamVjdE1lZGlhLzM5MzY5Mg==\n", "UHJvamVjdE1lZGlhLzM5MzQ3Nw==\n",
            "UHJvamVjdE1lZGlhLzM5MDc5MA==\n"])
        self.assertTrue(response)

if __name__ == '__main__':
    unittest.main()
