# An example to get the remaining rate limit using the Github GraphQL API.
import os
import time
import demoji
import requests
import pandas as pd
import gql
from gql.transport.requests import RequestsHTTPTransport

from backend.ml.meedan_interface.utils import first_n_lines


headers = {
    "X-Check-Token": os.environ.get('MEEDAN_KEY'), "Content-Type": 'application/json'}

# Instantiate client for requests made on the graphQL


def init_meedan_client(fetch_schema=False, headers=headers):
    if headers['X-Check-Token'] is None:
        meedan_key = os.environ.get('MEEDAN_KEY')
        if meedan_key is None:
            print('WARNING: COULD NOT LOAD MEEDAN KEY, QUERIES WILL FAIL')

    gql_transport = RequestsHTTPTransport(
        url='https://check-api.checkmedia.org/api/graphql',
        headers=headers,
    )
    meedan_client = gql.Client(
        transport=gql_transport,
        fetch_schema_from_transport=fetch_schema,  # increases loading time
    )
    return meedan_client


gql_client = init_meedan_client()


# Send a query_string to the graphQL server
# This function implements two different method (through gql or requests) that same thing
# because there was a weird bug with certain queries
def meedan_query(query_string, gql_client=gql_client, headers=headers, method='gql'):
    if method == 'gql':
        if gql_client is None:
            gql_client = init_meedan_client(fetch_schema=False)
        try:
            gql_query = gql.gql(query_string)
        except:
            print('GQL error formatting query: \n', query_string)
        try:
            response = gql_client.execute(gql_query)
        except:
            print('Server error on GQL query',
                  gql_query, '\nerror:\n', response)
        return response

    if method == 'requests':
        request = requests.post('https://check-api.checkmedia.org/api/graphql',
                                json={'query': query_string}, headers=headers)
        if request.status_code == 200:
            return request.json()['data']
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(
                request.status_code, query_string))


# Get all the tags
def get_all_tags():
    query_string = '''
    {
      team(id: 2014) {
        tag_texts {
          edges {
            node {
              id, text, updated_at, created_at, dbid, tags_count
            }
          }
        }
      }
    }
    '''
    response = meedan_query(query_string)
    tags = response['team']['tag_texts']['edges']
    tags = pd.DataFrame([x['node'] for x in tags])
    return tags


def get_all_tags():
    query_string = '''
    {
      team(id: 2014) {
        team_tasks {
          edges {
            node {
              id
              description, label, type, updated_at, created_at, dbid
            }
          }
        }
      }
    }
    '''
    response = meedan_query(query_string)
    tags = response['team']['tag_texts']['edges']
    tags = pd.DataFrame([x['node'] for x in tags])
    return tags


def get_all_medias(max_medias=0):
    query_string = '''
    {
      team(id: 2014) {
        name
        projects_count
        projects {
          edges {
            node {
              title
              project_medias {
                edges {
                  node {
                    title, id, dbid, project_id, description, language, status, last_seen, metadata
                  }
                }
              }
            }
          }
        }
      }
    }
    '''
    if max_medias > 0:
        query_string = query_string.replace('project_medias {',
                                            'project_medias (first: ' + str(max_medias) + ') {')
    if max_medias < 0:
        query_string = query_string.replace('project_medias {',
                                            'project_medias (last: ' + str(-max_medias) + ') {')

    gql_query = gql.gql(query_string)
    all_medias = gql_client.execute(gql_query)
    meedan_lists = all_medias['team']['projects']['edges']
    df_list = []
    for meedan_list in meedan_lists:
        medias = pd.DataFrame(
            [x['node'] for x in meedan_list['node']['project_medias']['edges']])
        medias['list_name'] = meedan_list['node']['title']
        df_list.append(medias)
    df = pd.concat(df_list)
    df = df.set_index('dbid')  # else index are duplicated
    df = df.rename(columns={'project_id': 'list_dbid'})
    # add youtube urls
    urls = pd.Series(index=df.index)
    uris = pd.Series(index=df.index)
    for index, row in df.metadata.items():
        try:
            urls[index] = row['url']
            uris[index] = row['external_id']
        except:
            print('Error retreiving video url at index', index)
    df['url'] = urls
    df['uri'] = uris
    return df


def update_video_description(media_id=1,
                             list_dbid=3111,
                             updated_title='Default Title',
                             updated_description='no description',
                             gql_client=gql_client):
    list_dbid = str(list_dbid)
    media_id = media_id.split('==')[0]  # keep only the part before the ==
    # formatting is pain in the ass https://stackoverflow.com/questions/42444130/python-multi-line-json-and-variables
    query_string = '''
    mutation {
      updateProjectMedia( input: {
        project_id: %s,
        clientMutationId: "1",
        id: "%s==\\n",
        metadata: "{\\"description\\": \\"%s\\", \\"title\\": \\"%s\\"}"
      }) {
        project_media {
          title
          description
          id
        }
      }
    }
    ''' % (list_dbid, media_id, updated_description, updated_title)
    try:
        gql_query = gql.gql(query_string)
    except:
        print('gql_query string error')
        pass
    gql_query_fields = gql_query.definitions[0].selection_set.selections[0].arguments[0].value.fields
    for gql_field in gql_query_fields:
        if gql_field.name.value == 'metadata':
            gql_field.value.value = gql_field.value.value.replace('\n', '\\n')
            gql_field.value.value = gql_field.value.value.replace('\t', '\\t')
            gql_field.value.value = gql_field.value.value.replace('\s', '\\s')
            gql_field.value.value = demoji.replace(
                gql_field.value.value, '*_*')
    try:
        response = gql_client.execute(gql_query)
        return response
    except:
        print('Gql update error')
        return 1


# add a video, and update its descprition right after
# not working until update_video_description works
def add_and_update_video(youtube_uri, list_dbid, n_description_lines=10):
    try:
        raw_response = add_uri_to_list(youtube_uri, list_dbid)
    except:
        print('Could not add video', youtube_uri)
        return 1
    API_response = raw_response['createProjectMedia']['project_media']
    author_name = API_response['metadata']['oembed']['author_name']
    author_url = API_response['metadata']['oembed']['author_url']
    metatags = pd.DataFrame(API_response['metadata']['raw']['metatags'])
    yt_video_tags = metatags[metatags.property == 'og:video:tag'].content
    tags_string = ' - '.join(yt_video_tags)
    description = API_response['description']
    title = API_response['title']
    media_id = API_response['id']
    updated_title = author_name + ' || ' + title
    trimmed_description = first_n_lines(description, n=n_description_lines)
    updated_description = '|' + tags_string + '|\n' + trimmed_description + \
        '\n \n Channel: ' + author_name + ' | ' + author_url
    updated_description = updated_description.replace(
        '\n', '\\n').replace('\t', '\\t').replace('"', '')
    updated_title = updated_title.replace(
        '\n', '\\n').replace('\t', '\\t').replace('"', '')
    print('Sleeping 15 sec to let system update')
    time.sleep(3)
    updated = update_video_description(
        media_id, list_dbid, updated_title, updated_description)
    return updated


def add_uri_to_list(youtube_uri, list_dbid):
    youtube_url = 'https://www.youtube.com/watch?v=' + youtube_uri
    query = '''
    mutation create
    {
        createProjectMedia(
            input: {
                project_id: list_dbid,
                url: "youtube_url",
                clientMutationId: "1"})
        {
            project_media { title, id, description, metadata}
        }
    }
    '''
    query = query.replace('list_dbid', str(list_dbid))
    query = query.replace('youtube_url', youtube_url)
    new_element = meedan_query(query_string=query)
    return(new_element)


def get_all_lists(headers=headers):
    list_query = '''
    query {
      me {
        current_team {
          projects {
            edges {
              node {
                title, dbid
              }
            }
          }
        }
      }
    }
    '''
    all_lists = meedan_query(query_string=list_query)
    all_lists = all_lists['me']['current_team']['projects']['edges']
    all_lists = [x['node'] for x in all_lists]
    all_lists = pd.DataFrame(all_lists)
    return all_lists


def parse_media_metadata(row):
    metadata = row.metadata
    o_author_name = metadata['oembed']['author_name']
    o_author_url = metadata['oembed']['author_url']
    author_name = metadata['author_name']
    author_url = metadata['author_url']
    external_id = metadata['external_id']
    title = metadata['title']
    url = metadata['url']
