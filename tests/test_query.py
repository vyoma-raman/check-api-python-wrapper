import unittest
import sys
import os
from expected_response import xr_dbid_id, xr_list_names, xr_medias_count
sys.path.append('../check_api')
from meedan_interface_template import MeedanAPI

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

    @unittest.expectedFailure
    def test_bad_query(self):
        sample_query = 'query -> me -> current_team -> id -> dbid'
        response = self.meedan_api.execute(sample_query)
        self.assertEqual(response, xr_dbid_id, 'Formatting error')

    @unittest.expectedFailure
    def test_fail(self):
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
        response = self.meedan_api.execute(sample_query)
        self.assertEqual(response, xr_medias_count, 'Incorrect field error')

if __name__ == '__main__':
    unittest.main()
