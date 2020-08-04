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
To access the Meedan Check API python wrapper, make sure you have access to an API key and **owner permissions**. Once you have this API key, you can instantiate a `MeedanAPI` class to work with.

```
from meedan_interface import MeedanAPI

api_key = os.environ.get('MEEDAN_KEY')
meedan_api = MeedanAPI(api_key)
```

The python wrapper can access basic Meedan Check API functionality.

#### Adding Videos

#### Deleting Videos

#### Collecting Annotations

### FAQ
**How can I update my permissions?**

**Why am I getting a server error on GQL query?**

### Credits
Written by Vyoma Raman and Nicole Zhu
