#!/usr/bin/python3.7

import asyncio, pprint

from helpers import Aiogoogle, user_creds, client_creds, api_key, email

from aiogoogle.excs import HTTPError
from aiofiles import os

async def list_events():
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        calendar_v3 = await aiogoogle.discover('calendar', 'v3')
        req = calendar_v3.events.list(calendarId='primary')
        res = await aiogoogle.as_user(
            req
        )
    pprint.pprint(res)

if __name__ == '__main__':
    asyncio.run(list_events())