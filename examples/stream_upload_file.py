#!/usr/bin/python3.7

'''
Scopes Required:

* https://www.googleapis.com/auth/drive
* https://www.googleapis.com/auth/drive.file

API explorer link:

* https://developers.google.com/apis-explorer/#p/drive/v3/drive.files.create
'''

import asyncio

from helpers import Aiogoogle, user_creds, client_creds


class MyFile:
    @staticmethod
    async def read():
        return b'Hello World'


async def stream_upload_file():
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        # Create API
        drive_v3 = await aiogoogle.discover("drive", "v3")

        req = drive_v3.files.create(
            pipe_from=MyFile(),
            fields="id"
        )

        # Upload file
        upload_res = await aiogoogle.as_user(req)
        print(f"Uploaded stream file successfully.\nFile ID: {upload_res['id']}")

if __name__ == "__main__":
    asyncio.run(stream_upload_file())
