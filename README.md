# Check API Python Wrapper

## Description
This is a Python wrapper for the [Meedan Check API](https://github.com/meedan/check-api).

## Table of Contents
* [Dependencies](###Dependencies)
* [Usage](###Usage)
* [Frequently Asked Questions](###FAQ)
* [Credits](###Credits)

### Dependencies
To use this Python package, make sure the [GraphQL Python Client (gql)](https://pypi.org/project/gql/) is installed.
```
pip install gql
```

### Usage

#### Getting Started
To access the Meedan Check API Python wrapper, make sure you have access to an API key and **owner permissions**. Once you have this API key, you can instantiate a `MeedanAPI` class to work with. Your team slug is found in the Check URL: checkmedia.org/**team-slug**/

```
from meedan_interface import MeedanAPI

api_key = os.environ.get('MEEDAN_KEY')
meedan_api = MeedanAPI(api_key, "team-slug")
```

The Python wrapper can access basic Meedan Check API functionality.

#### Adding Videos

**Add a single video** to a particular list *(Note: cannot be added if item already exists in Check)*:

`meedan_api.add_video(uri, list_id)`
* `uri`: Unique video identifier. Last 11 digits of YouTube URL (ex. "5fQTJ_86IEs" in "youtube.com/watch?v=5fQTJ_86IEs")
* `list_id`: The name of the list to add the video to, or the corresponding 4 digit id. All list names and ids can be found with the following query
* Returns a dictionary containing `uri` as the key and Check's unique item id as the value

```
query {
  team(slug: "team-slug") {
    projects {
      edges {
        node {
          title
          dbid
        }
      }
    }
  }
}
```

**Add several videos** to one list:

`meedan_api.add_video_list(uri_list, list_id)`
* `uri_list`: List of uris. See `uri` description above
* `list_id`: See description above
* Returns a dictionary (description above) with a key-value pair for every video in the list

**Restore a single video** from trash:

`meedan_api.restore_video(item_id)`
* `item_id`: See description above
* Returns *True*

**Restore several videos** from trash:

`meedan_api.restore_video_list(item_ids)`
* `item_id_list`: See description above
* Returns *True*

#### Removing Videos

Send a **single video to trash** *(Note: does not remove the video from Check)*:

`meedan_api.trash_video(item_id)`
* `item_id`: Check's unique item id (returned in dictionary when adding videos) 
* Returns *True*

Send **several videos to trash**:

`meedan_api.trash_video_list(item_ids)`
* `item_id_list`: List of item ids. See `item_id` description above
* Returns *True*

Permanently **delete single video**:

`meedan_api.delete_video(item_id)`
* `item_id`: See description above
* Returns *True*

Permanently **delete several videos**:

`meedan_api.delete_video_list(item_ids)`
* `item_id_list`: See description above
* Returns *True*

#### Collecting Annotations

`meedan_api.collect_annotations(in_trash)`
* `in_trash`: *Optional* argument to specify whether to collect annotations for items that have been trashed. Default *False*
* Returns nested dictionary of annotations. Entry format:

```
{ uri : { 'status' : verification_status, 'tags' : [tag1, tag2, ...], 'last_updated' : datetime, 'notes' : [note1, note2, ...], 'last_updated_by' : username } }
```

### FAQs
**How can I run a query?**

To run your own queries, use either [Check's GraphiQL](https://check-api.checkmedia.org/graphiql) (must have CloudFlare access) or the `execute` function within this package.

*Execute*

This function is not intended for significant user interaction and is best for running simple queries to access id information and user permissions. It returns the API response as a dictionary.

```
query_string = """ insert query here """
meedan_api.execute(query_string)
```

**How can I update my permissions?**

Have a member of your project who has owner permissions run the following mutation.

```
mutation {
  updateTeamUser(input: { clientMutationId: "1", id: "team-user-id", role: "owner"}) {
    team_user {
      role
      status
      id
      team {
        name
      }
    }
  }
}
```

Current user permissions and team user ids can be found by running the following query.

```
query {
  team(slug: "team-slug") {
    team_users {
      edges {
        node {
          user {
            name
          }
          role
          id
        }
      }
    }
  }
}
```

**Why am I getting a server error on GQL query?**

### Credits
Written by Vyoma Raman and Nicole Zhu
