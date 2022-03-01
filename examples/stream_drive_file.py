#!/usr/bin/python3.7

'''
Scopes Required:

* https://www.googleapis.com/auth/drive
* https://www.googleapis.com/auth/drive.file

API explorer link:

* https://developers.google.com/apis-explorer/#p/drive/v3/drive.files.get
'''

import asyncio
import sys

from helpers import Aiogoogle, user_creds, client_creds

usage = """
Usage:

    argv1: ID of the file you want to stream (see hint)

Hint:

    run list_drive_files.py to list the names of the files you own alongside their IDs

Example:

    List the id of "my_old_archive.tar.gz" by running:

        ./list_drive_files | grep my_old_archive.tar.gz
        0Bw9MwYF2OXbSc0d0ZmNlRjVhMmM: myold_archive.tar.gz

    Now run:

        ./stream_drive_file.py 0Bw9MwYF2OXbSc0d0ZmNlRjVhMmM
"""


class MyFile:
    @staticmethod
    async def write(data: bytes):
        print(data)


async def stream_file(file_id):
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover("drive", "v3")

        # Stream the file
        await aiogoogle.as_user(
            drive_v3.files.get(fileId=file_id, pipe_to=MyFile(), alt="media")
        )


if __name__ == "__main__":
    try:
        file_id = sys.argv[1]
    except IndexError:
        print(usage)
        sys.exit(1)
    asyncio.run(stream_file(file_id))
