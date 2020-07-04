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
        response = None
        try:
            gql_query = gql.gql(query_string)
        except:
            print('GQL error formatting query: \n', query_string)
        try:
            response = self.client.execute(gql_query)
        except:
            print('Server error on GQL query', gql_query, '\nerror:\n', response)
        return response
        # response = requests.get(url = self.endpoint, params = query_string, headers = self.headers)
        # if response.status_code != 200:
        #     raise Exception('Server-reported error: {}\nGiven query:\n{}'.format(response.status_code, query_string))
        # try:
        #     return response.json()['data']
        # except Exception as e:
        #     print('Response formating error:\n', e)

    def add_video(self, uri, list_id):
        """
        :str uri: 11 character string that serve as video identifier in a youtube url
        :param list_id: str or int, refering to the list name or list_dbid
        :return: some confirmation
        """
        # forge the query_string and then send with self.execute
        # catch the 'item already exists' error
        pass

    def remove_video(self, item_id, list_id):
        """
        :str item_id: a unique identifier for the item, there a several ones (dbid, id, uri) not sure which is best for this purpose
        :param list_id: str or int, refering to the list name or list_dbid
        :return: some confirmation
        """
        # similar to above. Catch error if item not in the list
        # if the API doesnt let you identify items by uri, another identifier (like dbid) can be used instead
        pass
