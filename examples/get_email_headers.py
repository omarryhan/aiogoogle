#!/usr/bin/python3.7

'''
Scopes Required:

* "https://www.googleapis.com/auth/gmail.readonly"
'''

import asyncio

from helpers import Aiogoogle, user_creds, client_creds


async def get_email_headers():
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as google:
        gmail = await google.discover("gmail", "v1")

        response = await google.as_user(
            gmail.users.messages.list(userId="me", maxResults=1)
        )
        key = response["messages"][0]["id"]
        email = await google.as_user(gmail.users.messages.get(userId="me", id=key))
    headers = email["payload"]["headers"]
    for header in headers:
        print(f"{header['name']}: {header['value']}")


if __name__ == "__main__":
    asyncio.run(get_email_headers())
