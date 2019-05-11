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

## Quick Start

**List your Google Drive Files**

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

**List your Google Calendar events using [Trio](https://github.com/python-trio/trio)**

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

**List your Youtube videos using [curio](https://github.com/dabeaz/curio)**

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

## Documentation 📑

readthedocs: https://aiogoogle.readthedocs.io/en/latest/

## Setup ⚙️

```bash
$ pip install aiogoogle
```

## Contact 📧

I currently work as a freelance software devloper. Like my work and got a gig for me?

Want to hire me fulltime? Send me an email @ omarryhan@gmail.com

## Buy me a coffee ☕

**Bitcoin:** 3NmywNKr1Lzo8gyNXFUnzvboziACpEa31z

**Ethereum:** 0x1E1400C31Cd813685FE0f6D29E0F91c1Da4675aE

**Bitcoin Cash:** qqzn7rsav6hr3zqcp4829s48hvsvjat4zq7j42wkxd

**Litecoin:** MB5M3cE3jE4E8NwGCWoFjLvGqjDqPyyEJp

**Paypal:** https://paypal.me/omarryhan
