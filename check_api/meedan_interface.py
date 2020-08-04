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
    #   - Potential future changes: create Python "item" class to mirror Meedan's "item" 
    #     object so that title, description, etc. are easily accessible

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
        response = self.execute(query_string)
        video_data = response["createProjectMedia"]["project_media"]
        video_id = video_data["id"]
        return {uri: video_id}

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

    def add_video_list(self, uri_list, list_id, slug):
        """
        Adds each video in the given list to given project list.
        :list uri_list: list of strings that serve as video identifier in a youtube url
        :param list_id: str or int, refering to the list name or list_dbid
        :str slug: name of team found in URL, ex: checkmedia.org/ischool-hrc => ischool-hrc
        :return: dictionary with uri as key and projectmedia id as value
        """
        if len(uri_list) == 0:
            raise Exception("Please specify item(s) to add.")
        id_dict = {}
        for uri in uri_list:
            try:
                success = self.add_video(uri, list_id, slug)
                id_dict.update(success)
            except:
                print('Could not add video "' + uri + '".\nAdded items:')
                return id_dict
        return id_dict

    def mutate_video_list(self, item_id_list, function):
        """
        Helper function to perform some mutation on a list of videos.
        :list item_id_list: list of ids of videos to mutate (add, )
        :return: some confirmation
        """
        if len(item_id_list) == 0:
            raise Exception("Please specify item(s) to mutate.")
        for item_id in item_id_list:
            success = function(item_id)
            assert success, "Mutation could not be performed for item_id " + self.format_item(item_id) + "."
        return True

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

    def collect_annotations(self, slug, in_trash=False):
        """
        Gets the uri, id, dbid, verification status, tags, verifier, verification date, and 
        comments of each annotation
        :param list_id: str or int, refering to the list name or list_dbid
        :str slug: name of team found in URL, ex: checkmedia.org/ischool-hrc => ischool-hrc
        :bool in_trash: whether to return the annotations for items in trash
        :return: annotations
        """
        annotations_query = '''query {
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
        }''' % (slug)
        response = self.execute(annotations_query)
        return self.format_response(response, in_trash)

    def collect_comments(self, dbid):
        """
        Helper function that gets comments on a project_media
        :int dbid: Meedan's dbid identifier for a particular piece of content
        :return: list of comment texts
        """
        print("dbid:",dbid)
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
        print(query_string)
        response = self.execute(query_string)
        return [edge['node']['text'] for edge in util.strip(response)]

    def format_response(self, response, in_trash):
        """
        Helper function that formats comments and other annotations
        :dict response: response from server
        :bool comment: whether the response is from collect_comments
        """
        all_nodes = []
        for node in util.strip(response):
            all_nodes.extend(util.strip(node))
        cleaned = {}
        for node in all_nodes:
            node = node["node"]
            title = node.pop("title")
            cleaned[title] = node
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
