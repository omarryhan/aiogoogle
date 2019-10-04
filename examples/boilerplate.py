#!/usr/bin/python3.7

import asyncio
import pprint

from helpers import Aiogoogle, user_creds, client_creds


async def method_resource():
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        name_version = await aiogoogle.discover("name", "version")
        req = name_version.resource.method(parameterOne="uno", parameterTwo="deus")
        res = await aiogoogle.as_user(req)
    pprint.pprint(res)


if __name__ == "__main__":
    asyncio.run(method_resource())
