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
        self.meedan_api = MeedanAPI(self.key)
        warnings.simplefilter("ignore", ResourceWarning)

    def test(self):
        # response = self.meedan_api.add_video("DqZS89jFCFg", "#Wietske", "ischool-hrc")
        # response = self.meedan_api.collect_annotations("#Wietske", 'ischool-hrc')
        # print(response)
        query_string = """query {
          team(slug: "ischool-hrc") {
            projects {
              edges {
                node {
                  title
                  dbid
                  project_medias {
                    edges {
                      node {
                        media {
                          url
                        }
                        title
                        tags {
                          edges {
                            node {
                              tag_text
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }"""
        print(self.meedan_api.execute(query_string))

if __name__ == '__main__':
    unittest.main()
