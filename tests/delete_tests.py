import unittest
import sys
import os
import warnings
sys.path.append('../check_api')
from meedan_interface import MeedanAPI

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.key = os.environ.get('MEEDAN_KEY')
        self.meedan_api = MeedanAPI(self.key)
        warnings.simplefilter("ignore", ResourceWarning)

    #TODO: Finish fleshing out tests once method is completed
    def test_delete(self):
        response = self.meedan_api.delete_video("UHJvamVjdE1lZGlhLzM5MzY5Mg==\n")
        self.assertTrue(response)

    def test_delete_list(self):
        response = self.meedan_api.delete_video_list(["UHJvamVjdE1lZGlhLzM5MzcwNA==\n", "UHJvamVjdE1lZGlhLzM5MzcwMw==\n",
            "UHJvamVjdE1lZGlhLzM5MzcwMg==\n"])
        self.assertTrue(response)

if __name__ == '__main__':
    unittest.main()
