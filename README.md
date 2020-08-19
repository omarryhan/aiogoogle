<p align="center">
  <img src="https://i2.wp.com/googlediscovery.com/wp-content/uploads/google-developers.png" alt="Logo" title="Aiogoogle" height="150" width="200"/>
  <p align="center">
    <a href="https://travis-ci.org/omarryhan/aiogoogle"><img alt="Build Status" src="https://travis-ci.org/omarryhan/aiogoogle.svg?branch=master"></a>
    <a href="https://github.com/omarryhan/aiogoogle"><img alt="Software License" src="https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square"></a>
    <a href="https://github.com/python/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg" /></a>
    <a href="https://pepy.tech/badge/aiogoogle"><img alt="Downloads" src="https://pepy.tech/badge/aiogoogle"></a>
    <a href="https://pepy.tech/badge/aiogoogle/month"><img alt="Monthly Downloads" src="https://pepy.tech/badge/aiogoogle/month"></a>
  </p>
</p>

# Aiogoogle

Async **Discovery Service** Client +

Async **Google OAuth2** Client +

Async **Google OpenID Connect (Social Sign-in)** Client

Aiogoogle makes it possible to access most of Google's public APIs which include:

- Google Calendar API
- Google Drive API
- Google Contacts API
- Gmail API
- Google Maps API
- Youtube API
- Translate API
- Google Sheets API
- Google Docs API
- Gogle Analytics API
- Google Books API
- Google Fitness API
- Google Genomics API
- Kubernetes Engine API
- And [more](https://developers.google.com/apis-explorer)

## Setup ⚙️

```bash
$ pip install aiogoogle
```

## Google Account Setup

1. Create a project: [Google’s APIs and Services dashboard](https://console.cloud.google.com/projectselector/apis/dashboard)
2. Enable an API: [API Library](https://console.cloud.google.com/apis/library)
3. Create credentials: [Credentials wizard](https://console.cloud.google.com/apis/credentials/wizard?)
4. Pick an API: [Google's API explorer](https://developers.google.com/apis-explorer/)

## Authentication

There are **3** main authentication schemes you can use with Google's discovery service:

1. **OAuth2**

    Should be used whenever you want to access personal information from user accounts.

    Also, Aiogoogle supports Google OpenID connect which is a superset of OAuth2. (Google Social Signin)

2. **API key**

    Suitable when accessing Public information.
    
    A simple secret string, that you can get from Google's Cloud Console

    **Note:**
        
        For most personal information, an API key won't be enough.

        You should use OAuth2 instead.

3. **Service Accounts**

    A service account is a special kind of account that belongs to an application or a virtual machine (VM) instance, not a person.
    
    **Note:**
        
        Not yet supported by Aiogoogle

## OAuth2 Primer

Oauth2 serves as an authorization framework. It supports **4** main flows:

1. **Authorization code flow** **Only flow suppoerted*:
    - [RFC6749 section 4.1](https://tools.ietf.org/html/rfc6749#section-4.1)

2. **Client Credentials Flow**:
    - Similar to the **API key** authentication scheme provided by Aiogoogle, so use it instead.
    - [RFC6749 section 4.4](https://tools.ietf.org/html/rfc6749#section-4.4)

3. **Implicit Grant Flow**:
    - Not supported.
    - [RFC6749 section 4.2](https://tools.ietf.org/html/rfc6749#section-4.2)

4. **Resource Owner Password Credentials Flow**:
    - Not supported.
    - [RFC6749 section 4.3](https://tools.ietf.org/html/rfc6749#section-4.2)

Since Aiogoogle only supports **Authorization Code Flow** which happens to fit most use cases, let's dig a little in to it:

## Authorization Code Flow

There are **3** main parties involved in this flow:

1. **User**: 
    - The application consumer.
    - represented as [``aiogoogle.UserCreds``](https://aiogoogle.readthedocs.io/en/latest/#aiogoogle.auth.creds.UserCreds)
2. **Client**:
    - The Application owner.
    - represented as [``aiogoogle.ClientCreds``](https://aiogoogle.readthedocs.io/en/latest/#aiogoogle.auth.creds.ClientCreds)
3. **Resource Server**:
    - The service that aiogoogle acts as a client to. e.g. Google Analytics, Youtube, etc. 

Here's a nice ASCII chart showing how this flow works [RFC6749 section 4.1 Figure 3](https://tools.ietf.org/html/rfc6749#section-4.1.1>)

    +----------+
    | Resource |
    |   Owner  |
    |          |
    +----------+
        ^
        |
        (B)
    +----|-----+          Client Identifier      +---------------+
    |         -+----(A)-- & Redirection URI ---->|               |
    |  User-   |                                 | Authorization |
    |  Agent  -+----(B)-- User authenticates --->|     Server    |
    |          |                                 |               |
    |         -+----(C)-- Authorization Code ---<|               |
    +-|----|---+                                 +---------------+
    |    |                                           ^      v
    (A)  (C)                                         |      |
    |    |                                           |      |
    ^    v                                           |      |
    +---------+                                      |      |
    |         |>---(D)-- Authorization Code ---------'      |
    |  Client |          & Redirection URI                  |
    |         |                                             |
    |         |<---(E)----- Access Token -------------------'
    +---------+       (w/ Optional Refresh Token)


## Authorization examples (the examples require Sanic HTTP Server)

**Get user credentials using OAuth2 (Authorization code flow)** [full example](https://github.com/omarryhan/aiogoogle/blob/master/examples/auth(production_unsafe)/oauth2.py)

```python 3.7
import webbrowser

from sanic import Sanic, response
from sanic.exceptions import ServerError

from aiogoogle import Aiogoogle
from aiogoogle.auth.utils import create_secret


EMAIL = "client email"
CLIENT_CREDS = {
    "client_id": '...',
    "client_secret": '...',
    "scopes": ['...'],
    "redirect_uri": "http://localhost:5000/callback/aiogoogle",
}
state = create_secret()  # Shouldn't be a global hardcoded variable.

LOCAL_ADDRESS = "localhost"
LOCAL_PORT = "5000"

app = Sanic(__name__)
aiogoogle = Aiogoogle(client_creds=CLIENT_CREDS)


@app.route("/authorize")
def authorize(request):
    if aiogoogle.oauth2.is_ready(CLIENT_CREDS):
        uri = aiogoogle.oauth2.authorization_url(
            client_creds=CLIENT_CREDS,
            state=state,
            access_type="offline",
            include_granted_scopes=True,
            login_hint=EMAIL,
            prompt="select_account",
        )
        return response.redirect(uri)
    else:
        raise ServerError("Client doesn't have enough info for Oauth2")


@app.route("/callback/aiogoogle")
async def callback(request):
    if request.args.get("error"):
        error = {
            "error": request.args.get("error"),
            "error_description": request.args.get("error_description"),
        }
        return response.json(error)
    elif request.args.get("code"):
        returned_state = request.args["state"][0]
        if returned_state != state:
            raise ServerError("NO")
        full_user_creds = await aiogoogle.oauth2.build_user_creds(
            grant=request.args.get("code"), client_creds=CLIENT_CREDS
        )
        return response.json(full_user_creds)
    else:
        # Should either receive a code or an error
        return response.text("Something's probably wrong with your callback")


if __name__ == "__main__":
    webbrowser.open("http://" + LOCAL_ADDRESS + ":" + LOCAL_PORT + "/authorize")
    app.run(host=LOCAL_ADDRESS, port=LOCAL_PORT, debug=True)
```

**OpenID Connect (Social signin)** [full example](https://github.com/omarryhan/aiogoogle/blob/master/examples/auth(production_unsafe)/openid_connect.py)

```python 3.7
import webbrowser
import pprint

from sanic import Sanic, response
from sanic.exceptions import ServerError

from aiogoogle import Aiogoogle
from aiogoogle.auth.utils import create_secret

EMAIL = "..."
CLIENT_CREDS = {
    "client_id": "...",
    "client_secret": "...",
    "scopes": ["openid", "email"],
    "redirect_uri": "http://localhost:5000/callback/aiogoogle",
}
state = (
    create_secret()
)  # Shouldn't be a global or a hardcoded variable. should be tied to a session or a user and shouldn't be used more than once
nonce = (
    create_secret()
)  # Shouldn't be a global or a hardcoded variable. should be tied to a session or a user and shouldn't be used more than once


LOCAL_ADDRESS = "localhost"
LOCAL_PORT = "5000"

app = Sanic(__name__)
aiogoogle = Aiogoogle(client_creds=CLIENT_CREDS)


@app.route("/authorize")
def authorize(request):
    if aiogoogle.openid_connect.is_ready(CLIENT_CREDS):
        uri = aiogoogle.openid_connect.authorization_url(
            client_creds=CLIENT_CREDS,
            state=state,
            nonce=nonce,
            access_type="offline",
            include_granted_scopes=True,
            login_hint=EMAIL,
            prompt="select_account",
        )
        return response.redirect(uri)
    else:
        raise ServerError("Client doesn't have enough info for Oauth2")


@app.route("/callback/aiogoogle")
async def callback(request):
    if request.args.get("error"):
        error = {
            "error": request.args.get("error"),
            "error_description": request.args.get("error_description"),
        }
        return response.json(error)
    elif request.args.get("code"):
        returned_state = request.args["state"][0]
        if returned_state != state:
            raise ServerError("NO")
        full_user_creds = await aiogoogle.openid_connect.build_user_creds(
            grant=request.args.get("code"),
            client_creds=CLIENT_CREDS,
            nonce=nonce,
            verify=False,
        )
        full_user_info = await aiogoogle.openid_connect.get_user_info(full_user_creds)
        return response.text(
            f"full_user_creds: {pprint.pformat(full_user_creds)}\n\nfull_user_info: {pprint.pformat(full_user_info)}"
        )
    else:
        # Should either receive a code or an error
        return response.text("Something's probably wrong with your callback")


if __name__ == "__main__":
    webbrowser.open("http://" + LOCAL_ADDRESS + ":" + LOCAL_PORT + "/authorize")
    app.run(host=LOCAL_ADDRESS, port=LOCAL_PORT, debug=True)
```

**API key example**

No need for an example because it's very simple. Just get an API key from your Google management console and pass it on to your Aiogoogle instance. Like this:

```python
aiogoogle = Aiogoogle(api_key='...')
```

## Discovery Service

Most of Google’s public APIs are documented/discoverable by a single API called the Discovery Service.

Google’s Discovery Serivce provides machine readable specifications known as discovery documents (similar to [Swagger/OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/master/examples/v3.0/petstore.yaml)). e.g. [Google Books](https://www.googleapis.com/discovery/v1/apis/books/v1/rest).

Aiogoogle is a Pythonic wrapper for discovery documents.

For a list of supported APIs, visit: [Google’s APIs Explorer](https://developers.google.com/apis-explorer/).

## Discovery docs and the ``Aiogoogle`` object explained

To understand how to navigate a discovery service/document and access the API endpoints that you desire using the [Aiogoogle object](https://aiogoogle.readthedocs.io/en/latest/#id2), it is **highly recommended** that you read [this](https://aiogoogle.readthedocs.io/en/latest/#discovery-docs-and-the-aiogoogle-object-explained) section in the docs.


## Quick Examples

**List your Google Drive Files** [full example](https://github.com/omarryhan/aiogoogle/blob/master/examples/list_drive_files.py)

```python 3.7
import asyncio
from aiogoogle import Aiogoogle


user_creds = {'access_token': '....', 'refresh_token': '....'}

async def list_files():
    async with Aiogoogle(user_creds=user_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover('drive', 'v3')
        full_res = await aiogoogle.as_user(
            drive_v3.files.list(),
            full_res=True
        )

    async for page in full_res:
        for file in page['files']:
            print(file['name'])

asyncio.run(list_files())
```

**Shorten a URL using an API key as the authentication scheme of choice**

```python 3
import asyncio
from aiogoogle import Aiogoogle
from pprint import pprint

async def shorten_url(long_urls):
    async with Aiogoogle(api_key=api_key) as google:
        url_shortener = await google.discover('urlshortener', 'v1')
        short_urls = await google.as_api_key(

            url_shortener.url.insert(
                json=dict(
                    longUrl=long_url[0]
                ),

            url_shortener.url.insert(
                json=dict(
                    longUrl=long_url[1]
                )
        )
    return short_urls

short_urls = asyncio.run(
    shorten_url(
        ['https://www.google.com', 'https://www.google.org']
    )
)
pprint(short_urls)
```

```json
[
    {
        "kind": "urlshortener#url",
        "id": "https://goo.gl/Dk2j",
        "longUrl": "https://www.google.com/"
    },
    {
        "kind": "urlshortener#url",
        "id": "https://goo.gl/Dk23",
        "longUrl": "https://www.google.org/"
    }
]
```

**List your Google Calendar events using [Trio](https://github.com/python-trio/trio)** | [full example](https://github.com/omarryhan/aiogoogle/blob/master/examples/list_calendar_events_trio.py)

```bash
$ pip install aiogoogle[trio_asks]
```

```python 3.7
import trio
from aiogoogle import Aiogoogle
from aiogoogle.sessions.trio_asks_session import TrioAsksSession


user_creds = {'access_token': '....', 'refresh_token': '....'}

async def list_events():
    async with Aiogoogle(
        user_creds=user_creds,
        session_factory=TrioAsksSession,
    ) as aiogoogle:
        calendar_v3 = await aiogoogle.discover("calendar", "v3")
        events = await aiogoogle.as_user(
            calendar_v3.events.list(calendarId="primary"), full_res=True
        )
    async for page in events:
        print(page)

trio.run(list_events)
```

**List your Youtube videos using [Curio](https://github.com/dabeaz/curio)** | [full example](https://github.com/omarryhan/aiogoogle/blob/master/examples/list_calendar_events_curio.py)

```bash
$ pip install aiogoogle[curio_asks]
```

```python 3.7
import curio
from aiogoogle import Aiogoogle
from aiogoogle.sessions.curio_asks_session import CurioAsksSession


user_creds = {'access_token': '....', 'refresh_token': '....'}

async def list_playlists():
    async with Aiogoogle(
        user_creds=user_creds,
        session_factory=CurioAsksSession,
    ) as aiogoogle:
        youtube_v3 = await aiogoogle.discover("youtube", "v3")
        req = youtube_v3.playlists.list(part="snippet", mine=True)
        res = await aiogoogle.as_user(req)
    print(res)

curio.run(list_playlists())
```

**Pagination**

```python 3
async def list_files():
    async with Aiogoogle(user_creds=user_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover('drive', 'v3')
        full_res = await aiogoogle.as_user(
            drive_v3.files.list(),
            full_res=True
        )
    async for page in full_res:
        for file in page['files']:
            print(file['name'])

asyncio.run(list_files())
```

## Documentation 📑

readthedocs: https://aiogoogle.readthedocs.io/en/latest/

## Contribute 🙋

There's a bunch you can do to help regardless of your experience level:

1. **Features, chores and bug reports:**

    Please refer to the Github issue tracker where they are posted. 

2. **Examples:**

    You can add examples to the examples folder

3. **Testing:**

    Add more tests. The library is currently a bit undertested

## Development notes

### To upload a new version

**Change the version in:**

1. `setup.py`
2. root `__init__.py`
3. `docs/conf.py`

**Build:**

```sh
python setup.py sdist
```

**Upload:**

```sh
twine upload dist/{the_new_version}
```

### To install the local version of the aiogoogle instead of the latest one on Pip

```sh
pip uninstall aiogoogle
```

```sh
cd {cloned_aiogoogle_repo_with_your_local_changes}
```

```sh
pip install -e .
```

Now you can import aiogoogle from anywhere in your FS and make it use your local version
