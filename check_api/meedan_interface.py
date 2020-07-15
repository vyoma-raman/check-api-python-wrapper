import gql
import util
from gql.transport.requests import RequestsHTTPTransport

class MeedanAPI:
    def __init__(self, key): # add more arguments if needed
        """
        :param key:
        """
        self.key = key
        self.endpoint = 'https://check-api.checkmedia.org/api/graphql'
        self.headers = {"X-Check-Token": self.key, "Content-Type" : 'application/json'}
        self.client = self.create_client()

    # NOTES:
    #   - Suggestion: define parsers separately to parse the API responses (see YouTubeAPI package)
    #   - Potential future changes: design functions to take iterables or single values; create Python "item" class to
    #     mirror Meedan's "item" object so that title, description, etc. are easily accessible

    def create_client(self):
        # helper function to instantiate client for requests made with gql
        if self.key is None:
            print("WARNING: COULD NOT LOAD MEEDAN KEY, QUERIES WILL FAIL")

        #TODO: catch any errors that might result from improper headers
        gql_transport=RequestsHTTPTransport(
            url=self.endpoint,
            headers=self.headers,
        )
        client = gql.Client(
            transport=gql_transport,
            fetch_schema_from_transport=False, # maybe change later
        )
        return client

    def execute(self, query_string):
        """
        :str query_string: # the query_string such as in graphIQL
        :return: API response (maybe as a dictionary)
        """
        # this function should not be user facing, but all user facing functions below should call it to execute queries.
        # gql seems pretty good for that purpose (see from my previous code) but not necessary. Alternatively, forge http
        # requests 'by hand' and send them with the 'requests' package
        # 1) depending on how you want to send the queries, the query_string might need some formating
        #    for instance, the escape char \ need to be doubled with gql
        # 2) send the formatted query string to self.endpoint using package requests, gql, or which ever package you
        #    find best appropriate to query graphQL APIs. Use self.headers to authenticate
        # Catch and print API errors clearly to assist with debugging other functions

        response, gql_query = None, None
        try:
            gql_query = gql.gql(query_string)
        except:
            raise SyntaxError('GQL error formatting query: ' + query_string)
        try:
            response = self.client.execute(gql_query)
        except Exception as e:
            raise Exception('Server error on GQL query: ' + query_string + ' Error: ' + str(e))
        return response

    def get_proj_id(self, slug, proj_dbid):
        """
        :str slug: name of team found in URL, ex: checkmedia.org/ischool-hrc => ischool-hrc
        :str or int proj_id: either the name of the list or the project dbid
        :str return: project dbid
        """
        if isinstance(proj_dbid, str):
            #queries for project names and their associated ID
            proj_query = '''query {
              team(slug: "%s") {
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
            ''' % (slug)
            response = self.execute(proj_query)
            # Extract list of projects
            proj_nodes = util.strip(response)
            # Create new dictionary where the project titles are the keys
            proj_dict = util.pivot_dict(proj_nodes, "title", "dbid")
            proj_dbid = proj_dict[proj_dbid]
        return str(proj_dbid)

    def format_item(self, item_id):
        """
        :param items_ids: accepts single item id string or nonempty list of item id strings
        :return: string of item or items, to be fed into query
        """
        return repr(item_id).replace("'", '"')

    def add_video(self, uri, list_id, slug):
        """
        :str uri: 11 character string that serve as video identifier in a youtube url
        :param list_id: str or int, refering to the list name or list_dbid
        :str slug: name of team found in URL, ex: checkmedia.org/ischool-hrc => ischool-hrc
        :return: some confirmation
        """
        url = 'https://www.youtube.com/watch?v=' + uri
        query_string = '''mutation {
          createProjectMedia(input: {
            clientMutationId: "1",
            project_id: %s,
            url: "%s",
          }) {
            project_media {
              dbid
            }
          }
        }''' % (self.get_proj_id(slug, list_id), url)
        #try to collect response. if exception raised, if error code 9, remove_video and try again. else, print error
        try:
            response = self.execute(query_string)
        except Exception as e:
            # if error code == 9:
                # get id of this item
                # call delete_video with this id in a list
                # try to execute this query again
            # else:
                # print error message
            print(e)
        #TODO: Parse response and return dbid as confirmation
        return response

    def add_video_list(self, uri_list, list_id, slug):
        """
        :list uri_list: list of strings that serve as video identifier in a youtube url
        :param list_id: str or int, refering to the list name or list_dbid
        :str slug: name of team found in URL, ex: checkmedia.org/ischool-hrc => ischool-hrc
        :return: some confirmation
        """
        # TODO: get dbid of team
        for uri in uri_list:
            response = self.add_video(uri, list_id, slug)
            # TODO: if response != dbid:
                # raise Exception
        return # dbid

    def trash_video(self, item_ids, list_id=None):
        """
        :list item_ids: non-empty list of ids of items to trash such as ["UHJvamVjdE1lZGlhLzM5MDc5MA==\n"]
        :param list_id: str or int, refering to the list name or list_dbid
        :return: some confirmation
        """
        if len(item_ids) == 0:
            raise Exception("Please specify item(s) to send to trash.")
        if list_id:
            for item in item_ids:
                # TODO: raise Exception if item not in list
                pass
        query_string = '''mutation {
          updateProjectMedia(input: {
            clientMutationId: "1",
            id: %s,
            ids: %s,
            archived: 1
          }) {
            affectedIds
          }
        }''' % (self.format_item(item_ids[0]), self.format_item(item_ids))
        response = self.execute(query_string)
        #TODO: Parse response and return that affectedIds == item_ids as confirmation
        return response

    def restore_video(self, item_ids):
        """
        :list item_ids: non-empty list of ids of items to remove such as ["UHJvamVjdE1lZGlhLzM5MDc5MA==\n"]
        :return: some confirmation
        """
        if len(item_ids) == 0:
            raise Exception("Please specify item(s) to restore from trash.")
        query_string = '''mutation {
          updateProjectMedia(input: {
            clientMutationId: "1",
            id: %s,
            ids: %s,
            archived: 0
          }) {
            affectedIds
          }
        }''' % (self.format_item(item_ids[0]), self.format_item(item_ids))
        response = self.execute(query_string)
        #TODO: Parse response and return that affectedIds == item_ids as confirmation
        return response

    def delete_video(self, item_ids):
        """
        :list item_ids: non-empty list of ids of items to remove such as ["UHJvamVjdE1lZGlhLzM5MDc5MA==\n"]
        :return: some confirmation
        """
        if len(item_ids) == 0:
            raise Exception("Please specify item(s) to permanently remove.")
        elif len(item_ids) == 1:
            query_string = '''mutation {
              destroyProjectMedia(input: {
                clientMutationId: "1", 
                id: %s
              }) { 
                deletedId,
                team {
                  name
                }
              }
            }''' % (self.format_item(item_ids[0]))
        else:
            query_string = '''mutation {
              destroyProjectMedia(input: {
                clientMutationId: "1",
                id: %s,
                ids: %s
              }) { 
                affectedIds,
                team {
                  name
                }
              }
            }''' % (self.format_item(item_ids[0]), self.format_item(item_ids))
        response = self.execute(query_string)
        #TODO: Parse response and return team name
        return response

    def collect_annotations(self, list_id):
        """
        :param list_id: str or int, refering to the list name or list_dbid
        :return: annotations
        """
        pass