import unittest
import sys
import os
sys.path.append('../')
from check_api.meedan_interface_template import MeedanAPI

# Suggestion: Put expected response into external file that we can pull from to reduce clutter
class TestAPI(unittest.TestCase):

    def setUp(self):
        self.key = os.environ.get('MEEDAN_KEY')
        self.meedan_api = MeedanAPI(self.key)

    def test_teaminfo(self):
        sample_query = '''query {
          me {
            current_team {
              id
              dbid
            }
          }
        }
        '''
        # expected response from graphIQL
        expected_response = {
            "me": {
                "current_team": {
                    "dbid": 2014,
                    "id": "VGVhbS8yMDE0\n"
                }
            }
        }
        response = self.meedan_api.execute(sample_query)
        self.assertEqual(response, expected_response)

    def test_getprojects(self):
        sample_query = '''query {
          me {
            current_team {
              projects {
                edges {
                  node {
                    title
                  }
                }
              }
            }
          }
        }
        '''
        expected_response = {
            "me": {
                "current_team": {
                    "projects": {
                        "edges": [
                            {
                                "node": {
                                    "title": "#Avani"
                                }
                            },
                            {
                                "node": {
                                    "title": "complete"
                                }
                            },
                            {
                                "node": {
                                    "title": "debunks"
                                }
                            },
                            {
                                "node": {
                                    "title": "false positives"
                                }
                            },
                            {
                                "node": {
                                    "title": "#Iland"
                                }
                            },
                            {
                                "node": {
                                    "title": "#Janine"
                                }
                            },
                            {
                                "node": {
                                    "title": "#Jean"
                                }
                            },
                            {
                                "node": {
                                    "title": "#Michael"
                                }
                            },
                            {
                                "node": {
                                    "title": "#Nicole"
                                }
                            },
                            {
                                "node": {
                                    "title": "religious_edge_cases"
                                }
                            },
                            {
                                "node": {
                                    "title": "#Rose"
                                }
                            },
                            {
                                "node": {
                                    "title": "#Scott"
                                }
                            },
                            {
                                "node": {
                                    "title": "test"
                                }
                            },
                            {
                                "node": {
                                    "title": "true positives"
                                }
                            },
                            {
                                "node": {
                                    "title": "#Uma"
                                }
                            },
                            {
                                "node": {
                                    "title": "#Vyoma"
                                }
                            },
                            {
                                "node": {
                                    "title": "#Wendy"
                                }
                            },
                            {
                                "node": {
                                    "title": "#Wietske"
                                }
                            },
                            {
                                "node": {
                                    "title": "#Zuzanna"}}]}}}}
        response = self.meedan_api.execute(sample_query)
        self.assertEqual(response, expected_response)


if __name__ == '__main__':
    unittest.main()
