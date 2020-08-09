# Check API Python Wrapper

## Description
This is a Python wrapper for the [Meedan Check API](https://github.com/meedan/check-api).

## Table of Contents
* [Dependencies](###Dependencies)
* [Usage](###Usage)
* [Frequently Asked Questions](###FAQ)
* [Credits](###Credits)

## Dependencies
To use this Python package, make sure the [GraphQL Python Client (gql)](https://pypi.org/project/gql/) is installed.
```
pip install gql
```

## Usage

### Getting Started
To access the Meedan Check API Python wrapper, make sure you have access to an [API key](https://github.com/meedan/check/wiki/Authentication-and-authorization-on-Check-API) and **owner permissions**. You will also need to know your team slug which can be found in the Check URL: checkmedia.org/**team-slug**/

Once you have the API key and team slug, you can instantiate a `MeedanAPI` class to work with.

```
from meedan_interface import MeedanAPI

api_key = os.environ.get("MEEDAN_KEY")
meedan_api = MeedanAPI(api_key, "team-slug")
```

The Python wrapper can access basic Meedan Check API functionality.

### Adding Videos

**Add a single video** to a particular list *(Note: A video cannot be added if it already exists in Check)*:


```
meedan_api.add_video(uri, list_id)
```
* `uri`: Unique video identifier. Last 11 digits of YouTube URL (ex. "5fQTJ_86IEs" in "youtube.com/watch?v=5fQTJ_86IEs")
* `list_id`: The name of the list to add the video to, or the corresponding 4 digit ID. See [FAQ](###FAQs) for more information on finding the ID.
* Returns a dictionary containing `uri` as the key and Check's unique item id as the value

**Add several videos** to one list:

```
meedan_api.add_video_list(uri_list, list_id)
```
* `uri_list`: List of uris. See `uri` description above
* `list_id`: See description above
* Returns a dictionary (description above) with a key-value pair for every video in the list

### Restoring Videos

**Restore a single video** from trash:

```
meedan_api.restore_video(item_id)
```
* `item_id`: See description above
* Prints confirmation after successfully restoring the video

**Restore several videos** from trash:

```
meedan_api.restore_video_list(item_ids)
```
* `item_id_list`: See description above
* Prints confirmation after successfully restoring each video

### Removing Videos

Send a **single video to trash** *(Note: does not remove the video from Check)*:

`meedan_api.trash_video(item_id)`
* `item_id`: Check's unique item id (returned in dictionary when adding videos)
* Prints confirmation after successfully trashing the video

Send **several videos to trash**:

`meedan_api.trash_video_list(item_ids)`
* `item_id_list`: List of item ids. See `item_id` description above
* Prints confirmation after successfully trashing each video

Permanently **delete single video**:

`meedan_api.delete_video(item_id)`
* `item_id`: See description above
* Prints confirmation after successfully deleting the video
* In rare cases, this query may experience issues deleting media that have been trashed. If so, simply restore the media in question and try again

Permanently **delete several videos**:

`meedan_api.delete_video_list(item_ids)`
* `item_id_list`: See description above
* Prints confirmation after successfully deleting each video

### Collecting Annotations

`meedan_api.collect_annotations(in_trash)`

*(Note: This query may take several minutes to run)*
* `in_trash`: *Optional* argument to specify whether to collect annotations for items that have been trashed. Default *False*
* Returns nested dictionary of annotations. Entry format:

```
{ uri : { "status" : verification_status, "tags" : [tag1, tag2, ...], "last_updated" : datetime, "notes" : [note1, note2, ...], "last_updated_by" : username } }
```

## FAQs

**How can I run a query?**

To run your own queries, use either [Check's GraphiQL](https://check-api.checkmedia.org/graphiql) (must have CloudFlare access) or the `execute` function within this package.

This function is not intended for significant user interaction and is best for running simple queries to access id information and user permissions. It returns the API response as a dictionary.

```
query_string = """ insert query here """
meedan_api.execute(query_string)
```

**How can I find the corresponding ID of my list?**

All list names and ids can be found by running the following query:

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

**How can I update my permissions?**

Have a member of your project who has owner permissions run the following mutation:

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

Current user permissions and team user ids can be found by running the following query:

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

**Why am I getting a server error code on GQL query?**

Error Code 1:
* Server connection error
* *To Solve*: [See Meedan's writeup](https://github.com/meedan/check-api/blob/master/doc/api.md)

Error Code 5:

`"message": "No permission to update/delete Dynamic"`
* The user you are running the query with does not have the necessary permissions to mutate the media
* *To Solve*: See above for instructions to update permissions

`"message": "undefined method 'project' for #<Link:0x00007f34c5919af0>\nDid you mean? projects\n projects="`
* Meedan does not recognize the id entered into the query
* *To Solve*: Make sure to use the `id` under the ProjectMedia node rather than the `id` under `media`

Error Code 9:

`"message": "This item already exists"`
* The item you are attempting to add already exists in the project
* *To Solve*: If necessary to re-add, use `delete_video` to remove the item. Then add again.


## Credits
Written by Vyoma Raman and Nicole Zhu
