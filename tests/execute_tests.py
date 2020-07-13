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
        response = self.meedan_api.execute(sample_query)
        self.assertEqual(response, xr_dbid_id, 'Should not error')

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
        response = self.meedan_api.execute(sample_query)
        self.assertEqual(response, xr_list_names, 'Should not error')

    def test_bad_format(self):
        sample_query = 'query -> me -> current_team -> id -> dbid'
        self.assertRaises(SyntaxError, lambda: self.meedan_api.execute(sample_query))

    def test_server_fail(self):
        sample_query = '''query {
          me {
            current_team {
              project {
                edges {
                  node {
                    medias_count
                  }
                }
              }
            }
          }
        }
        '''
        self.assertRaises(Exception, lambda: self.meedan_api.execute(sample_query))

    def test_descriptions(self):
        sample_query = '''query {
          me {
            current_team {
              projects {
                edges {
                  node {
                    project_medias (first:2) {
                      edges {
                        node {
                          description
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        '''
        response = self.meedan_api.execute(sample_query)
        self.assertEqual(response['me']['current_team']['projects']['edges'][1], xr_descriptions, 'Should not error')

if __name__ == '__main__':
    unittest.main()
