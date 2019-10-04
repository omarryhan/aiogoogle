#!/usr/bin/python3.7

import asyncio
import pprint

from helpers import Aiogoogle, user_creds, client_creds


async def list_playlists():
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        youtube_v3 = await aiogoogle.discover("youtube", "v3")
        req = youtube_v3.playlists.list(part="snippet", mine=True)
        res = await aiogoogle.as_user(req)
    pprint.pprint(res)


if __name__ == "__main__":
    asyncio.run(list_playlists())
