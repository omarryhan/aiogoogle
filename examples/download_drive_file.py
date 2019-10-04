#!/usr/bin/python3.7

import asyncio
import sys
import os

from helpers import Aiogoogle, user_creds, client_creds

usage = """
Usage:

    argv1: ID of the file you want to download (see hint)
    argv2: Full path of the dir to download to

Hint:

    run list_drive_files.py to list the names of the files you own alongside their IDs

Example:

    List the id of "my_old_archive.tar.gz" by running:

        ./list_drive_files | grep my_old_archive.tar.gz
        0Bw9MwYF2OXbSc0d0ZmNlRjVhMmM: myold_archive.tar.gz

    Now run:
    
        ./download_drive_file.py 0Bw9MwYF2OXbSc0d0ZmNlRjVhMmM /home/omar/Desktop
"""


async def download_file(file_id, dir_path):
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover("drive", "v3")

        # First get the name of the file
        info_res = await aiogoogle.as_user(drive_v3.files.get(fileId=file_id))

        # Make full path
        file_name = info_res["name"]
        full_path = os.path.join(dir_path, file_name)

        # Second download the file
        await aiogoogle.as_user(
            drive_v3.files.get(fileId=file_id, download_file=full_path, alt="media"),
            full_res=True,
        )

        print("Downloaded file to {} successfully!".format(full_path))


if __name__ == "__main__":
    try:
        file_id = sys.argv[1]
        dir_path = sys.argv[2]
    except IndexError:
        print(usage)
        sys.exit(1)
    asyncio.run(download_file(file_id, dir_path))
