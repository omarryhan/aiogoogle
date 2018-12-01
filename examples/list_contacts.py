#!/usr/bin/python3.7

import asyncio, pprint

from helpers import Aiogoogle, user_creds, client_creds, api_key, email

async def list_contacts():
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        contacts_list = []
        people_v1 = await aiogoogle.discover('people', 'v1')
        req = people_v1.people.connections.list(resourceName='people/me', personFields='names,phoneNumbers', pageToken='^CAAQ6t60t_YsGgYKAghkEAI')
        while req is not None:
            contacts = await aiogoogle.as_user(
                req,
                full_resp=True,
            )
            for connection in contacts.json['connections']:
                phone_nums = connection.get('phoneNumbers')
                if phone_nums:
                    num = phone_nums[0].get('canonicalForm')
                else:
                    num = None
                contacts_list.append(
                    {connection['names'][0]['displayName']: num}
                )
            req = contacts.next_page()

    pprint.pprint(contacts_list)
    print('Length:')
    print(len(contacts_list))

if __name__ == '__main__':
    asyncio.run(list_contacts())