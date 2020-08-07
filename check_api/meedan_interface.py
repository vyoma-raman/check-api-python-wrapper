import gql
import util
from gql.transport.requests import RequestsHTTPTransport

class MeedanAPI:
    def __init__(self, key, slug):
        """
        :param key: API key
        """
        self.key = key
        self.slug = slug
        self.endpoint = 'https://check-api.checkmedia.org/api/graphql?team=' + self.slug
        self.headers = {"X-Check-Token": self.key, "Content-Type" : 'application/json'}
        self.client = self.create_client()

    # HELPER FUNCTION

    def create_client(self):
        """
        Helper function to instantiate client using gql.
        :return: client for requests
        """
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

    # USER-FACING AND HELPER FUNCTION

    def execute(self, query_string):
        """
        Executes the given GraphQL query. Not usually user-facing, but called by all user-facing functions.
        :str query_string: the string of the query to run, such as in GraphiQL
        :dict return: API response
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

    # HELPER FUNCTION

    def get_proj_id(self, proj_dbid):
        """
        Given a project list id or title, returns a string form of the list id formatted for GraphQL query.
        :param proj_dbid: str or int, either the name of the list or the project dbid
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
            ''' % (self.slug)
            response = self.execute(proj_query)

            # Extract list of projects
            proj_nodes = util.strip(response)

            # Create new dictionary where the project titles are the keys
            proj_dict = util.pivot_dict(proj_nodes, "title", "dbid")
            proj_dbid = proj_dict[proj_dbid]
        return str(proj_dbid)

    # USER-FACING FUNCTION

    def add_video(self, uri, list_id):
        """
        Adds the given YouTube video to the front of the given project list.
        :str uri: 11 character string that serve as video identifier in a youtube url
        :param list_id: str or int, refering to the list name or list_dbid
        :dict return: single-item dictionary with uri as key and id as value
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
        }''' % (self.get_proj_id(list_id), url)
        response = self.execute(query_string)
        video_data = response["createProjectMedia"]["project_media"]
        video_id = video_data["id"]
        return {uri: video_id}

    # HELPER FUNCTION

    def update_video(self, item_id, archive):
        """
        Helper function to trash or restore videos with the given id.
        :str item_id: id of item to trash or restore
        :int archive: 0 to restore, 1 to trash
        :bool return: whether expected response was received
        """
        if len(item_id) == 0:
            raise Exception("Please specify item(s) to restore from trash.")
        query_string = '''mutation {
          updateProjectMedia(input: {
            clientMutationId: "1",
            id: %s,
            archived: %s
          }) { affectedId }
        }''' % (util.format_item(item_id), str(archive))
        response = self.execute(query_string)
        return response["updateProjectMedia"]["affectedId"] == item_id

    # USER-FACING FUNCTION

    def trash_video(self, item_id):
        """
        Sends given video to the trash.
        :str item_id: id of item to trash
        :bool return: result of calling update_video with specified arguments
        """
        self.update_video(item_id, 1)
        print("Item ID " + item_id + " has been sent to trash.")

    # USER-FACING FUNCTION

    def restore_video(self, item_id):
        """
        Restores given video from the trash.
        :str item_id: id of item to restore
        :bool return: result of calling update_video specified arguments
        """
        self.update_video(item_id, 0)
        print("Item with ID " + item_id + " has been restored.")

    # USER-FACING FUNCTION

    def delete_video(self, item_id):
        """
        Removes given video from the project.
        :str item_id: id of item to delete
        :bool return: whether expected response was received
        """
        query_string = '''mutation {
          destroyProjectMedia(input: {
            clientMutationId: "1",
            id: %s
          }) { deletedId }
        }''' % (util.format_item(item_id))
        try:
            self.execute(query_string)
            print("Item " + item_id + " has been deleted")
        except:
            # If item is in trash, attempts to restore video first before deleting
            self.restore_video(item_id)
            self.execute(query_string)
            print("Item " + item_id + " has been deleted")

    # USER-FACING FUNCTION

    def add_video_list(self, uri_list, list_id):
        """
        Adds each video in the given list to given project list.
        :list uri_list: list of strings that serve as video identifier in a youtube url
        :param list_id: str or int, refering to the list name or list_dbid
        :dict return: multi-item dictionary with uri as key and id as value
        """
        if len(uri_list) == 0:
            raise Exception("Please specify item(s) to add.")
        id_dict = {}
        for uri in uri_list:
            try:
                success = self.add_video(uri, list_id)
                id_dict.update(success)
            except Exception as e:
                print('Could not add video "' + uri + '".\nAdded items:', id_dict.values())
                print(e)
        return id_dict

    # HELPER FUNCTION

    def mutate_video_list(self, item_id_list, function):
        """
        Helper function to perform some mutation on a list of videos.
        :list item_id_list: list of ids of videos to mutate (add, )
        :bool return: True
        """
        if len(item_id_list) == 0:
            raise Exception("Please specify item(s) to mutate.")
        for item_id in item_id_list:
            success = function(item_id)
            assert success, "Mutation could not be performed for item_id " + util.format_item(item_id) + "."
        return True

    # USER-FACING FUNCTION

    def trash_video_list(self, item_id_list):
        """
        Sends each video in the given list to the trash.
        :list item_id_list: list of ids of videos to trash
        :bool return: result of calling mutate_video_list with specified arguments
        """
        self.mutate_video_list(item_id_list, self.trash_video)

    # USER-FACING FUNCTION

    def restore_video_list(self, item_id_list):
        """
        Restores each video in the given list from the trash.
        :list item_id_list: list of ids of videos to restore
        :bool return: result of calling mutate_video_list with specified arguments
        """
        self.mutate_video_list(item_id_list, self.restore_video)

    # USER-FACING FUNCTION

    def delete_video_list(self, item_id_list):
        """
        Deletes each video in the given list from the project.
        :list item_id_list: list of ids of videos to delete
        :bool return: result of calling mutate_video_list with specified arguments
        """
        return self.mutate_video_list(item_id_list, self.delete_video)

    # USER-FACING FUNCTION

    def collect_annotations(self, in_trash=False):
        """
        Gets the uri, id, dbid, verification status, tags, verifier, verification date, and
        comments of each annotation
        :param list_id: str or int, refering to the list name or list_dbid
        :bool in_trash: whether to return the annotations for items in trash
        :dict return: organized dictionary of annotations
        """
        query_string = '''query {
          team(slug: "%s") {
            projects {
              edges {
                node {
                  project_medias {
                    edges {
                      node {
                        media {
                          url
                        }
                        dbid
                        archived
                        title
                        status
                        tags {
                          edges {
                            node {
                              tag_text
                            }
                          }
                        }
                        updated_at
                        dynamic_annotations_verification_status {
                          edges {
                            node {
                              annotator {
                                name
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
          }
        }''' % (self.slug)
        response = self.execute(query_string)
        return self.format_response(response, in_trash)

    # HELPER FUNCTION

    def collect_comments(self, dbid):
        """
        Helper function that gets comments on a project_media
        :int dbid: Meedan's dbid identifier for a particular piece of content
        :list return: text of each comment
        """
        query_string = """query {
          project_media(ids: "%s") {
            annotations(annotation_type: "comment") {
              edges {
                node {
                  ... on Comment {
                    text
                  }
                }
              }
            }
          }
        }""" % (str(dbid))
        response = self.execute(query_string)
        text = [edge['node']['text'] for edge in util.strip(response)]
        return text

    # HELPER FUNCTION

    def format_response(self, response, in_trash):
        """
        Helper function that formats comments and other annotations
        :dict response: response from server
        :bool comment: whether the response is from collect_comments
        :dict return: response organized by media uri
        """
        # Create flat list of all nodes
        all_nodes = []
        for node in util.strip(response):
            all_nodes.extend(util.strip(node))
        # Create dictionary with 'title' as key and other fields as values
        cleaned = {}
        for node in all_nodes:
            node = node["node"]
            title = node.pop("title")
            cleaned[title] = node
        # Create single-nest dictionary from 'cleaned' with 'uri' as key
        reorganized = {}
        for k, v in cleaned.items():
            if in_trash or not v["archived"]:
                sub_dict = {}
                sub_dict['status'] = v["status"]
                tags = []
                for node in v["tags"]['edges']:
                    tags.append(node['node']['tag_text'])
                sub_dict['tags'] = tags
                sub_dict['last_updated'] = util.epoch_to_datetime(v["updated_at"])
                sub_dict['notes'] = self.collect_comments(v["dbid"])
                sub_dict['last_updated_by'] = v['dynamic_annotations_verification_status']['edges'][0]['node']['annotator']['name']
                reorganized[v["media"]['url'][-11:]] = sub_dict
        return reorganized
