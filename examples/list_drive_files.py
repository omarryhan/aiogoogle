#!/usr/bin/python3.7

import asyncio, pprint

from helpers import Aiogoogle, user_creds, client_creds, api_key, email


async def list_files():
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover("drive", "v3")
        res = await aiogoogle.as_user(drive_v3.files.list(), full_res=True)
    async for page in res:
        for file in page["files"]:
            print(f"{file.get('id')}: {file.get('name')}")


if __name__ == "__main__":
    asyncio.run(list_files())
