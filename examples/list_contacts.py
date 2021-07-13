#!/usr/bin/python3.7

'''
API explorer link:

* https://developers.google.com/apis-explorer/#p/people/v1/people.people.getBatchGet

Scopes Required:

* "https://www.googleapis.com/auth/contacts",
* "https://www.googleapis.com/auth/contacts.readonly",
* "https://www.googleapis.com/auth/plus.login",
* "https://www.googleapis.com/auth/user.addresses.read",
* "https://www.googleapis.com/auth/user.birthday.read",
* "https://www.googleapis.com/auth/user.emails.read",
* "https://www.googleapis.com/auth/user.phonenumbers.read",
* "https://www.googleapis.com/auth/userinfo.email",
* "https://www.googleapis.com/auth/userinfo.profile"
'''

import asyncio
import pprint

from helpers import Aiogoogle, user_creds, client_creds


async def list_contacts():
    aiogoogle = Aiogoogle(user_creds=user_creds, client_creds=client_creds)
    people_v1 = await aiogoogle.discover("people", "v1")

    contacts_list = []

    def append_connections(connections):
        for connection in connections:
            phone_nums = connection.get("phoneNumbers")
            if phone_nums:
                num = phone_nums[0].get("canonicalForm")
            else:
                num = None

            if "names" not in connection:
                name = ""
            else:
                name = connection["names"][0]["displayName"]
            contacts_list.append({name: num})

    async with aiogoogle:
        pages = await aiogoogle.as_user(
            people_v1.people.connections.list(
                resourceName="people/me", personFields="names,phoneNumbers"
            ),
            full_res=True,
        )
    async for page in pages:
        append_connections(page["connections"])

    pprint.pprint(contacts_list)
    print("Length:")
    print(len(contacts_list))


if __name__ == "__main__":
    asyncio.run(list_contacts())
