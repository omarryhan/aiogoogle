#!/usr/bin/python3.7

import trio, pprint

from helpers import Aiogoogle, user_creds, client_creds, api_key, email

from aiogoogle.sessions.trio_asks_session import TrioAsksSession

async def list_events():
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds, session_factory=TrioAsksSession) as aiogoogle:
        calendar_v3 = await aiogoogle.discover('calendar', 'v3')
        events = await aiogoogle.as_user(
            calendar_v3.events.list(calendarId='primary'),
            full_res=True,
        )
    async for page in events:
        pprint.pprint(page)

if __name__ == '__main__':
    trio.run(list_events)