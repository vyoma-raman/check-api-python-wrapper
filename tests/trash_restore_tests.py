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

    def test_trash_restore(self):
        self.meedan_api.trash_video("UHJvamVjdE1lZGlhLzM5NTEwMA==\n")
        self.meedan_api.restore_video("UHJvamVjdE1lZGlhLzM5NTEwMA==\n")

    def test_trash_restore_list(self):
        self.meedan_api.trash_video_list(["UHJvamVjdE1lZGlhLzM5NTEwMA==\n", "UHJvamVjdE1lZGlhLzM5NTA5OA==\n"])
        self.meedan_api.restore_video_list(["UHJvamVjdE1lZGlhLzM5NTEwMA==\n", "UHJvamVjdE1lZGlhLzM5NTA5OA==\n"])
        
if __name__ == '__main__':
    unittest.main()
