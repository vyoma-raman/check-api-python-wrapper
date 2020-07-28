import gql
import util
from gql.transport.requests import RequestsHTTPTransport

class MeedanAPI:
    def __init__(self, key): # add more arguments if needed
        """
        :param key: API key
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
        """
        Helper function to instantiate client using gql.
        :return: client for requests
        """
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
        Executes the given GraphQL query. Not user-facing, but called by user-facing functions.
        :str query_string: # the query_string such as in graphIQL
        :return: API response as a dictionary
        """        
        response, gql_query = None, None
        try:
            gql_query = gql.gql(query_string)
        except:
            raise SyntaxError('GQL error formatting query:\n' + query_string)
        try:
            response = self.client.execute(gql_query)
        except Exception as e:
            raise Exception('Server error on GQL query:\n' + query_string + '\nError:\n' + str(e))
        return response

    def get_proj_id(self, slug, proj_dbid):
        """
        Given a project list id or title, returns a string form of the list id formatted for GraphQL query.
        :str slug: name of team found in URL, ex: checkmedia.org/ischool-hrc => ischool-hrc
        :str or int proj_dbid: either the name of the list or the project dbid
        :str return: project dbid
        """
        if isinstance(proj_dbid, str):
            # queries for project names and their associated ID
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
        Given a string id for a project media, formats for insertion into GraphQL query.
        :param items_ids: accepts single item id string or nonempty list of item id strings
        :return: string of item to be fed into query
        """
        return repr(item_id).replace("'", '"')

    def add_video(self, uri, list_id, slug):
        """
        Adds the given YouTube video to the front of the given project list.
        :str uri: 11 character string that serve as video identifier in a youtube url
        :param list_id: str or int, refering to the list name or list_dbid
        :str slug: name of team found in URL, ex: checkmedia.org/ischool-hrc => ischool-hrc
        :return: bool of whether expected response was received
        """
        url = 'https://www.youtube.com/watch?v=' + uri
        query_string = '''mutation {
          createProjectMedia(input: {
            clientMutationId: "1",
            add_to_project_id: %s,
            url: "%s"
          }) {
            project_media {
              title
              id
            }
          }
        }''' % (self.get_proj_id(slug, list_id), url)
        response = None
        try:
            response = self.execute(query_string)
        except Exception as e:
            print(e)
        video_data = response["createProjectMedia"]["project_media"]
        title = video_data["title"]
        id = video_data["id"]
        return {title: id}

    def update_video(self, item_id, archive):
        """
        Helper function to trash or restore videos with the given id.
        :str item_id: id of item to trash or restore
        :int archive: 0 to restore, 1 to trash
        :return: bool of whether expected response was received
        """
        if len(item_id) == 0:
            raise Exception("Please specify item(s) to restore from trash.")
        query_string = '''mutation {
          updateProjectMedia(input: {
            clientMutationId: "1",
            id: %s,
            archived: %s
          }) { affectedId }
        }''' % (self.format_item(item_id), str(archive))
        response = self.execute(query_string)
        return response["updateProjectMedia"]["affectedId"] == item_id

    def trash_video(self, item_id):
        """
        Sends given video to the trash.
        :str item_id: id of item to trash
        :return: some confirmation
        """
        return self.update_video(item_id, 1)

    def restore_video(self, item_id):
        """
        Restores given video from the trash.
        :str item_id: id of item to restore
        :return: some confirmation
        """
        return self.update_video(item_id, 0)

    def delete_video(self, item_id):
        """
        Removes given video from the project.
        :str item_id: id of item to delete
        :return: some confirmation
        """
        query_string = '''mutation {
          destroyProjectMedia(input: {
            clientMutationId: "1",
            id: %s
          }) { deletedId }
        }''' % (self.format_item(item_id))
        response = None
        try:
            response = self.execute(query_string)
        except:
            self.restore_video(item_id)
            response = self.execute(query_string)
        return response["destroyProjectMedia"]["deletedId"] == item_id

    def mutate_video_list(self, item_id_list, function, list_id=None, slug=None):
        """
        Helper function to perform some mutation on a list of videos.
        :list item_id_list: list of ids of videos to mutate (add, )
        :return: some confirmation
        """
        if len(item_id_list) == 0:
            raise Exception("Please specify item(s) to mutate.")
        for item_id in item_id_list:
            if not list_id:
                success = function(item_id)
            else:
                success = function(item_id, list_id, slug)
            assert success, "Mutation could not be perform for item_id " + self.format_item(item_id) + "."
        return True

    def add_video_list(self, uri_list, list_id, slug):
        """
        Adds each video in the given list to given project list.
        :list uri_list: list of strings that serve as video identifier in a youtube url
        :param list_id: str or int, refering to the list name or list_dbid
        :str slug: name of team found in URL, ex: checkmedia.org/ischool-hrc => ischool-hrc
        :return: some confirmation
        """
        return self.mutate_video_list(uri_list, self.add_video, list_id, slug)

    def trash_video_list(self, item_id_list):
        """
        Sends each video in the given list to the trash.
        :list item_id_list: list of ids of videos to trash
        :return: some confirmation
        """
        return self.mutate_video_list(item_id_list, self.trash_video)

    def restore_video_list(self, item_id_list):
        """
        Restores each video in the given list from the trash.
        :list item_id_list: list of ids of videos to restore
        :return: some confirmation
        """
        return self.mutate_video_list(item_id_list, self.restore_video)

    def delete_video_list(self, item_id_list):
        """
        Deletes each video in the given list from the project.
        :list item_id_list: list of ids of videos to delete
        :return: some confirmation
        """
        return self.mutate_video_list(item_id_list, self.delete_video)

    def collect_annotations(self, list_id, slug):
        """
        :param list_id: str or int, refering to the list name or list_dbid
        :str slug: name of team found in URL, ex: checkmedia.org/ischool-hrc => ischool-hrc
        :return: annotations
        """
        annotations_query = '''query { project(id: "%s") {
            project_medias {
              edges {
                node {
                  title,
                  status,
                  tags {
                    edges {
                      node {
                        tag_text
                      }
                    }
                  },
                  media {
                    url
                  }
                }
              }
            }
          }
        }''' % (self.get_proj_id(slug, list_id))
        response = self.execute(annotations_query)
        cleaned = util.pivot_dict(util.strip(response), "title", ["media", "status", "tags"])
        reorganized = {}
        for k, v in cleaned.items():
            sub_dict = {}
            sub_dict['status'] = v[1]
            sub_dict['tags'] = []
            for node in v[2]['edges']:
                tags.append(node['node']['tag_text'])
            sub_dict['tags'] = tags
            reorganized[v[0]['url'][-11:]] = sub_dict
        return reorganized