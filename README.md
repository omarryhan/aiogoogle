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

## Setup ⚙️

```bash
$ pip install aiogoogle
```

## Quick Start

## Google Account Setup

1. Create a project: [Google’s APIs and Services dashboard](https://console.cloud.google.com/projectselector/apis/dashboard)
2. Enable an API: [API Library](https://console.cloud.google.com/apis/library)
3. Create credentials: [Credentials wizard](https://console.cloud.google.com/apis/credentials/wizard?)
4. Pick an API: [Google's API explorer](https://developers.google.com/apis-explorer/)

### Auth

**Get user credentials using OAuth2** [full example](https://github.com/omarryhan/aiogoogle/blob/master/examples/auth(production_unsafe)/oauth2.py)

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

**Social signin** [full example](https://github.com/omarryhan/aiogoogle/blob/master/examples/auth(production_unsafe)/openid_connect.py)

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
    "scopes": ["..."],
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

### Accessing APIs

**List your Google Drive Files** [full example](https://github.com/omarryhan/aiogoogle/blob/master/examples/list_drive_files.py)

```python 3.7
import asyncio
from aiogoogle import Aiogoogle


user_creds = {'access_token': 'an_access_token'}

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


user_creds = {'access_token': 'an_access_token'}

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


user_creds = {'access_token': 'an_access_token'}

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


## Contact 📧

I currently work as a freelance software devloper. Like my work and got a gig for me?

Want to hire me fulltime? Send me an email @ omarryhan@gmail.com

## Buy me a coffee ☕

**Bitcoin:** 3NmywNKr1Lzo8gyNXFUnzvboziACpEa31z

**Ethereum:** 0x1E1400C31Cd813685FE0f6D29E0F91c1Da4675aE

**Bitcoin Cash:** qqzn7rsav6hr3zqcp4829s48hvsvjat4zq7j42wkxd

**Litecoin:** MB5M3cE3jE4E8NwGCWoFjLvGqjDqPyyEJp

**Paypal:** https://paypal.me/omarryhan
