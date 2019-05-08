#!/usr/bin/python3.7

import asyncio, pprint, sys

from helpers import Aiogoogle, user_creds, client_creds, api_key, email


async def upload_file(full_path, new_name):
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        # Create API
        drive_v3 = await aiogoogle.discover("drive", "v3")

        # Upload file
        upload_res = await aiogoogle.as_user(
            drive_v3.files.create(upload_file=full_path, fields="id")
        )
        print("Uploaded {} successfully!".format(full_path))

        file_id = upload_res["id"]

        # Rename uploaded file
        await aiogoogle.as_user(
            drive_v3.files.update(fileId=file_id, json={"name": new_name})
        )
        print("Renamed {} to {} successfully!".format(full_path, new_name))


if __name__ == "__main__":
    usage = "\n\nUsage:\n\nargv1: Full file path of the file you want to upload. e.g.: /home/omar/Desktop/note.txt\n\narg2: Upload name"
    try:
        full_path = sys.argv[1]
        new_name = sys.argv[2]
    except IndexError:
        print(usage)
        sys.exit(1)
    asyncio.run(upload_file(full_path, new_name))
