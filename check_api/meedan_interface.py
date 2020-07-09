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

    def get_list_id(self, list_id):
        if isinstance(list_id, str):
            list_dict = { "#Avani": 3129, "complete": 3115, "debunks": 3163, "false positives": 3088, 
            "#Iland": 3140, "#Janine": 3112, "#Jean": 3138, "#Michael": 3132, "#Nicole": 3141, 
            "religious_edge_cases": 3162, "#Rose": 3130, "#Scott": 3133, "test": 3127, "true positives": 3109,
            "#Uma": 3136, "#Vyoma": 3135, "#Wendy": 3137, "#Wietske": 3111, "#Zuzanna": 3139 }
            list_id = list_dict[list_id]
        return str(list_id)

    def add_video(self, uri, list_id):
        """
        :str uri: 11 character string that serve as video identifier in a youtube url
        :param list_id: str or int, refering to the list name or list_dbid
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
        }''' % (self.get_list_id(list_id), url)
        #try to collect response. if error code 9, remove video and then try again
        response = self.execute(query_string)
        #TODO: Parse response and return dbid as confirmation
        return response

    def trash_video(self, item_ids):
        """
        :list item_id: non-empty list of ids of items to trash such as ["UHJvamVjdE1lZGlhLzM5MDc5MA==\n"]
        :return: some confirmation
        """
        # TODO: accept list_id and catch error if item not in list
        query_string = '''mutation {
          updateProjectMedia(input: {
            clientMutationId: "1",
            id: "%s",
            ids: %s,
            archived: 1
          }) {
            affectedIds
          }
        }''' % (item_ids[0], str(item_ids).replace("'", '"'))
        response = self.execute(query_string)
        #TODO: Parse response and return that affectedids == item_ids as confirmation
        return response

    def collect_annotations(self, list_id):
        """
        :param list_id: str or int, refering to the list name or list_dbid
        :return: annotations
        """
        pass