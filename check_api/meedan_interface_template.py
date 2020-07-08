import requests
import gql
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


    def add_video(self, uri, list_id):
        """
        :str uri: 11 character string that serve as video identifier in a youtube url
        :param list_id: str or int, refering to the list name or list_dbid
        :return: some confirmation
        """
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
        }''' % (str(list_id), uri)
        response = self.execute(query_string)
        #TODO: Parse response and return dbid as confirmation
        return response

    def remove_video(self, item_id, list_id):
        """
        :str item_id: a unique identifier for the item, there a several ones (dbid, id, uri) not sure which is best for this purpose
        :param list_id: str or int, refering to the list name or list_dbid
        :return: some confirmation
        """
        # similar to above. Catch error if item not in the list
        # if the API doesnt let you identify items by uri, another identifier (like dbid) can be used instead
        pass
