#!/usr/bin/python3.7

import curio
import pprint

from helpers import Aiogoogle, user_creds, client_creds

from aiogoogle.sessions.curio_asks_session import CurioAsksSession


async def list_events():
    async with Aiogoogle(
        user_creds=user_creds,
        client_creds=client_creds,
        session_factory=CurioAsksSession,
    ) as aiogoogle:
        calendar_v3 = await aiogoogle.discover("calendar", "v3")
        events = await aiogoogle.as_user(calendar_v3.events.list(calendarId="primary"))
    pprint.pprint(events)


if __name__ == "__main__":
    curio.run(list_events)
