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
    def test_restore(self):
        response = self.meedan_api.restore_video(["UHJvamVjdE1lZGlhLzM5MDkzMA==\n", "UHJvamVjdE1lZGlhLzM5MDkyOQ==\n"])

if __name__ == '__main__':
    unittest.main()
