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

    def test_strip(self):
        sample_query = '''query {
          team(slug: "ischool-hrc") {
            projects {
              edges {
                node {
                  title
                  id
                  dbid
                }
              }
            }
          }
        }
        '''
        response = self.meedan_api.execute(sample_query)
        nodes = util.strip(response)
        self.assertEqual(nodes, xr_nodes, "Strip function has failed")

        sample_dict = {"data": [{
            "team": {
                "edges": [{
                    "node": {
                        "name": "Nicole"
                            }
                        }]
                    }
            },
            {
                "team": {
                    "edges": [{
                        "node": {
                            "name": "Nicole"
                                }
                            }]
                        }
                }]
        }
        expected_list = [{'node': {'name': 'Nicole'}}, {'node': {'name': 'Nicole'}}]
        self.assertEqual(util.strip(sample_dict), expected_list, "Strip function failed on nested dictionaries")

    def test_pivot_dict(self):
        #Test pivoting where the value is a single entity
        self.assertEqual(util.pivot_dict(xr_nodes, "title", "dbid"), xr_pivot1, "Pivot function failed")
        #Test pivoting where the value is a list
        self.assertEqual(util.pivot_dict(xr_nodes, "title", ["dbid", "id"]), xr_pivot2, "Pivot function failed on value lists")

    def test_get_list_id(self):
        id = self.meedan_api.get_proj_id("#Nicole")
        self.assertEqual(id, "3141")
        id = self.meedan_api.get_proj_id("#Vyoma")
        self.assertEqual(id, "3135")

    def test_add_delete(self):
        video_id_dict = self.meedan_api.add_video("cc91EfoBh8A", "#Wietske")
        response = self.meedan_api.delete_video(list(video_id_dict.values())[0])
        self.assertTrue(response)

    def test_add_delete_list(self):
        response = self.meedan_api.delete_video_list(["UHJvamVjdE1lZGlhLzM5NTA5MA==\n", "UHJvamVjdE1lZGlhLzM5NTA4OQ==\n", "UHJvamVjdE1lZGlhLzM5NTA4OA==\n"])
        self.assertTrue(response)
        response = self.meedan_api.add_video_list(["XpqqjU7u5Yc", "DqZS89jFCFg", "I_izvAbhExY"], "#Wietske")
        self.assertTrue(response)

if __name__ == '__main__':
    unittest.main()
