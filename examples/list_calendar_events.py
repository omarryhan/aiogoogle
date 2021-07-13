#!/usr/bin/python3.7

'''
API explorer link:

* https://developers.google.com/apis-explorer/#p/calendar/v3/calendar.events.list?calendarId=primary&_h=2&

Scopes Required:

* "https://www.googleapis.com/auth/calendar",
* "https://www.googleapis.com/auth/calendar.events",
* "https://www.googleapis.com/auth/calendar.events.readonly",
* "https://www.googleapis.com/auth/calendar.readonly"
'''

import asyncio
import pprint

from helpers import Aiogoogle, user_creds, client_creds


async def list_events():
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        calendar_v3 = await aiogoogle.discover("calendar", "v3")
        pages = await aiogoogle.as_user(
            calendar_v3.events.list(calendarId="primary"), full_res=True
        )
    async for page in pages:
        pprint.pprint(page)


if __name__ == "__main__":
    asyncio.run(list_events())
