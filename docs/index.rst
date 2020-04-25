.. Aiogoogle documentation master file, created by
   sphinx-quickstart on Tue Nov 20 20:02:59 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Aiogoogle
===========

.. image:: _static/github_64.png
   :align: right
   :scale: 100 %
   :target: https://github.com/omarryhan/aiogoogle


Async **Discovery Service** Client` +

Async **Google OAuth2** Client +

Async **Google OpenID Connect (Social Sign-in)** Client

Aiogoogle makes it possible to access most of Google's public APIs including:

- Google Calendar API
- Google Drive API
- Google Contacts API
- Gmail API
- Google Maps API
- Youtube API
- Translate API
- Google Sheets API
- Google Docs API
- Gogle Analytics API
- Google Books API
- Google Fitness API
- Google Genomics API
- Kubernetes Engine API
- And `more <https://developers.google.com/apis-explorer>`_.

Discovery Service?
===================

Most of Google's public APIs are documented/discoverable by a single API called the Discovery Service.

Google's Discovery Serivce provides machine readable specifications known as discovery documents 
(similar to `Swagger/OpenAPI <https://github.com/OAI/OpenAPI-Specification/blob/master/examples/v3.0/petstore.yaml>`_). `e.g. Google Books <https://www.googleapis.com/discovery/v1/apis/books/v1/rest>`_.

In essence, Aiogoogle is a feature-rich, yet easy to use Pythonic wrapper for discovery documents.

For a list of supported APIs, visit: `Google's APIs Explorer <https://developers.google.com/apis-explorer/>`_.

Library Setup
=============

.. code-block:: bash

    $ pip install aiogoogle

Google Account Setup
====================

1. **Create a project:** `Google's APIs and Services dashboard <https://console.cloud.google.com/projectselector/apis/dashboard>`_.
2. **Enable an API:** `API Library <https://console.cloud.google.com/apis/library>`_.
3. **Create credentials:** `Credentials wizard <https://console.cloud.google.com/apis/credentials/wizard?>`_.
4. **Pick an API:** `Google's APIs Explorer <https://developers.google.com/apis-explorer/>`_ 

Authentication
================

There are 3 main authentication schemes you can use with Google's discovery service:

1. **OAuth2**
    Should be used whenever you want to access personal information from user accounts.

    Also, Aiogoogle supports Google OpenID connect which is a superset of OAuth2. (Google Social Signin)

2. **API key**
    Suitable when accessing Public information.
    
    A simple secret string, that you can get from Google's Cloud Console

    .. note::
        
        For most personal information, an API key won't be enough.

        You should use OAuth2 instead.

3. **Service Accounts**
    A service account is a special kind of account that belongs to an application or a virtual machine (VM) instance, not a person.
    
    .. note::
        
        Not yet supported by Aiogoogle

OAuth2 Primer
--------------

Oauth2 serves as an authorization framework. It supports four main flows:

1. **Authorization code flow**:
    - Only one supported by aiogoogle
    - `RFC6749 section 4.1  <https://tools.ietf.org/html/rfc6749#section-4.1>`_.

2. **Client Credentials Flow**:
    - Similar to API_KEY authentication so use API key authentication instead
    - `RFC6749 section 4.4  <https://tools.ietf.org/html/rfc6749#section-4.4>`_.

3. **Implicit Grant Flow**:
    - Not supported  
    - `RFC6749 section 4.2  <https://tools.ietf.org/html/rfc6749#section-4.2>`_.

4. **Resource Owner Password Credentials Flow**:
    - Not supported
    - `RFC6749 section 4.3  <https://tools.ietf.org/html/rfc6749#section-4.2>`_.

Since Aiogoogle only supports Authorization Code Flow, let's get a little in to it:

Authorization Code Flow
------------------------

There are 3 main parties are involved in this flow:

1. **User**: 
    - represented as ``aiogoogle.user_creds``
2. **Client**:
    - represented as ``aiogoogle.client_creds``
3. **Resource Server**:
    - The service that aiogoogle acts as a client to. e.g. Google Analytics, Youtube, etc. 

Here's a nice ASCII chart showing how this flow works `RFC6749 section 4.1 Figure 3 <https://tools.ietf.org/html/rfc6749#section-4.1.1>`_.::

    +----------+
    | Resource |
    |   Owner  |
    |          |
    +----------+
        ^
        |
        (B)
    +----|-----+          Client Identifier      +---------------+
    |         -+----(A)-- & Redirection URI ---->|               |
    |  User-   |                                 | Authorization |
    |  Agent  -+----(B)-- User authenticates --->|     Server    |
    |          |                                 |               |
    |         -+----(C)-- Authorization Code ---<|               |
    +-|----|---+                                 +---------------+
    |    |                                           ^      v
    (A)  (C)                                         |      |
    |    |                                           |      |
    ^    v                                           |      |
    +---------+                                      |      |
    |         |>---(D)-- Authorization Code ---------'      |
    |  Client |          & Redirection URI                  |
    |         |                                             |
    |         |<---(E)----- Access Token -------------------'
    +---------+       (w/ Optional Refresh Token)


OAuth2 Example
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

Full example here: https://github.com/omarryhan/aiogoogle/blob/master/examples/auth(production_unsafe)/oauth2.py

Install sanic

.. code-block:: bash

    pip install --upgrade sanic

.. warning::

    Do not copy and paste the following snippet as is.

    The error and return messages shown below are very verbose and aren't fit for production.

    If you're performing OAuth2 via Authorization Code Flow, you shouldn't hand the user their tokens.

.. hint:: Code reads from top to bottom

./app.py

.. code-block:: python3

    import sys, os, webbrowser, yaml, json

    from sanic import Sanic, response
    from sanic.exceptions import ServerError

    from aiogoogle import Aiogoogle
    from aiogoogle.auth.utils import create_secret

    try:
        with open("../keys.yaml", 'r') as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)
    except Exception as e:
        print('Rename _keys.yaml to keys.yaml')
        raise e

    EMAIL = config['user_creds']['email']
    CLIENT_CREDS = {
        'client_id': config['client_creds']['client_id'],
        'client_secret': config['client_creds']['client_secret'],
        'scopes': config['client_creds']['scopes'],
        'redirect_uri': 'http://localhost:5000/callback/aiogoogle',
    }
    state = create_secret()  # Shouldn't be a global hardcoded variable.


    LOCAL_ADDRESS = 'localhost'
    LOCAL_PORT = '5000'

    app = Sanic(__name__)
    aiogoogle = Aiogoogle(client_creds=CLIENT_CREDS)

    #----------------------------------------#
    #                                        #
    # **Step A (Check OAuth2 figure above)** #
    #                                        #
    #----------------------------------------#

    @app.route('/authorize')
    def authorize(request):
        uri = aiogoogle.oauth2.authorization_url(
            client_creds=CLIENT_CREDS, state=state, access_type='offline', include_granted_scopes=True, login_hint=EMAIL, prompt='select_account'
        )
        # Step A
        return response.redirect(uri)
    #----------------------------------------------#
    #                                              #
    # **Step B (Check OAuth2 figure above)**       #
    #                                              #
    #----------------------------------------------#
    # NOTE:                                        #
    #  you should now be authorizing your app @    #
    #   https://accounts.google.com/o/oauth2/      #
    #----------------------------------------------#

    #----------------------------------------------#
    #                                              #
    # **Step C, D & E (Check OAuth2 figure above)**#
    #                                              #
    #----------------------------------------------#

    # Step C
    # Google should redirect current_user to
    # this endpoint with a grant code
    @app.route('/callback/aiogoogle')
    async def callback(request):
        if request.args.get('error'):
            error = {
                'error': request.args.get('error'),
                'error_description': request.args.get('error_description')
            }
            return response.json(error)
        elif request.args.get('code'):
            returned_state = request.args['state'][0]
            # Check state
            if returned_state != state:
                raise ServerError('NO')
            # Step D & E (D send grant code, E receive token info)
            full_user_creds = await aiogoogle.oauth2.build_user_creds(
                grant = request.args.get('code'),
                client_creds = CLIENT_CREDS
            )
            return response.json(full_user_creds)
        else:
            # Should either receive a code or an error
            return response.text("Something's probably wrong with your callback")

    if __name__ == '__main__':
        webbrowser.open(
            'http://' + LOCAL_ADDRESS + ':' + LOCAL_PORT + '/authorize'
        )
        app.run(host=LOCAL_ADDRESS, port=LOCAL_PORT, debug=True)

OpenID Connect Example
,,,,,,,,,,,,,,,,,,,,,,,,,,,,

Full example here: https://github.com/omarryhan/aiogoogle/blob/master/examples/auth(production_unsafe)/openid_connect.py

.. warning::

    Do not copy and paste the following snippet as is.

    The error and return messages shown below are very verbose and aren't fit for production.

    If you're performing OAuth2 via Authorization Code Flow, you shouldn't hand the user their tokens.

.. code-block:: python3

    #!/usr/bin/python3.7

    import sys, os, webbrowser, yaml, json, pprint

    from sanic import Sanic, response
    from sanic.exceptions import ServerError

    from aiogoogle import Aiogoogle
    from aiogoogle.excs import HTTPError
    from aiogoogle.auth.utils import create_secret

    try:
        with open("../keys.yaml", 'r') as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)
    except Exception as e:
        print('Rename _keys.yaml to keys.yaml')
        raise e

    EMAIL = config['user_creds']['email']
    CLIENT_CREDS = {
        'client_id': config['client_creds']['client_id'],
        'client_secret': config['client_creds']['client_secret'],
        'scopes': config['client_creds']['scopes'],
        'redirect_uri': 'http://localhost:5000/callback/aiogoogle',
    }
    # Shouldn't be a global or a hardcoded variable.
    # Instead, should be tied to a session or a user and shouldn't be used more than once
    state = create_secret() 
    nonce = create_secret()


    LOCAL_ADDRESS = 'localhost'
    LOCAL_PORT = '5000'

    app = Sanic(__name__)
    aiogoogle = Aiogoogle(client_creds=CLIENT_CREDS)

    #----------------------------------------#
    #                                        #
    # **Step A (Check OAuth2 figure above)** #
    #                                        #
    #----------------------------------------#

    @app.route('/authorize')
    def authorize(request):
        if aiogoogle.openid_connect.is_ready(CLIENT_CREDS):
            uri = aiogoogle.openid_connect.authorization_url(
                client_creds=CLIENT_CREDS,
                state=state,
                nonce=nonce,
                access_type='offline',
                include_granted_scopes=True,
                login_hint=EMAIL,
                prompt='select_account'
            )
            # Step A
            return response.redirect(uri)
        else:
            raise ServerError(
                "Client doesn't have enough info for Oauth2"
            )

    #----------------------------------------------#
    #                                              #
    # **Step B (Check OAuth2 figure above)**       #
    #                                              #
    #----------------------------------------------#
    # NOTE:                                        #
    #  you should now be authorizing your app @    #
    #   https://accounts.google.com/o/oauth2/      #
    #----------------------------------------------#

    #----------------------------------------------#
    #                                              #
    # **Step C, D & E (Check OAuth2 figure above)**#
    #                                              #
    #----------------------------------------------#

    # Step C
    # Google should redirect current_user to
    # this endpoint with a grant code
    @app.route('/callback/aiogoogle')
    async def callback(request):
        if request.args.get('error'):
            error = {
                'error': request.args.get('error'),
                'error_description': request.args.get('error_description')
            }
            return response.json(error)
        elif request.args.get('code'):
            returned_state = request.args['state'][0]
            # Check state
            if returned_state != state:
                raise ServerError('NO')
            # Step D & E (D send grant code, E receive token info)
            full_user_creds = await aiogoogle.openid_connect.build_user_creds(
                grant=request.args.get('code'),
                client_creds=CLIENT_CREDS,
                nonce=nonce,
                verify=False
            )
            full_user_info = await aiogoogle.openid_connect.get_user_info(full_user_creds)
            return response.text(
                f"full_user_creds: {pprint.pformat(full_user_creds)}\n\nfull_user_info: {pprint.pformat(full_user_info)}"
            )
        else:
            # Should either receive a code or an error
            return response.text("Something's probably wrong with your callback")

    if __name__ == '__main__':
        webbrowser.open(
            'http://' + LOCAL_ADDRESS + ':' + LOCAL_PORT + '/authorize'
        )
        app.run(host=LOCAL_ADDRESS, port=LOCAL_PORT, debug=True)

Browsing a Google Discovery Service and making API calls
=========================================================

Now that you have figured out which authentication scheme you are going to use, let's make some API calls.

Assuming that you chose the: *Urlshortener-v1* API:

.. note::

    As of March 30, 2019, the Google URL shortening service was shut down.

Create a URL-shortener Google API instance
--------------------------------------------

.. code-block:: python3

    import asyncio
    from aiogoogle import Aiogoogle

    async def create_api(name, version):
        async with Aiogoogle() as google:
            return await google.discover(name, version)  # Downloads the API specs and creates an API object

    url_shortener = asyncio.run(
        create_api('urlshortener', 'v1')
    )

Structure of an API
----------------------

This is what a JSON representation of the discovery documen we downloaded looks like.

    ::

        Root
        |__ name
        |__ version
        |__ baseUrl
        |__ Global Parameters
        |__ Schemas
        |__ Resources
            |__ Resources
                |_ Resources
                    |_...
                |_ Methods
            |__ Methods
        |__ Methods
            |_ Path
            |_ Parameters
            |_ Request Body
            |_ Response Body

    `Full reference: <https://developers.google.com/discovery/v1/reference/apis>`_.

You don't have to worry about most of this. What's important to understand is how the discovery service is just a way to list *resources* and *methods*.

In the case of Youtube of the Youtube API for example, a resource can be: `videos` and a method would be list `list`.

The way you would access this is by executing: `aiogoogle.videos.list()`

A resource can also have a nested resource. e.g. `aiogoogle.videos.comments.list()`

There can also be top level methods that are not associated with any method. Though that's not common.

Finally, the only way you can get a data from the Google API is by calling a method. You can't call a resource and expect data.

Browse an API
-----------------

Back to the URL shortener API.

**Let's list the resources of the URL shortener API**:

.. code-block:: python3

    >>> url_shortener['resources']

    {
        'url': {

            'methods':

                'get': ...
                'insert': ...
                'list': ...
    }


**Now, let's browse the resource called `url`**

.. code-block:: python3

    >>> url_resource = url_shortener.url

    >>> url_resource.methods_available

**It has the following methods available to call**:

.. code-block:: python3

    ['get', 'insert', 'list']

**Sometimes resources have nested resources**

.. code-block:: python3

    >>> url_resource.resources_available

    []

This one doesn't.

**Let's inspect the method called `list` of the `url` resource**

.. code-block:: python3

    >>> list_url = url_resource.list

**Let's see what this method does**

.. code-block:: python3

    >>> list_url['description']

    "Retrieves a list of URLs shortened by a user."
    
**Cool, now let's see what are the optional parameters that this method takes**

.. code-block:: python3

    >>> list_url.optional_parameters

    ['projection', 'start_token', 'alt', 'fields', 'key', 'oauth_token', 'prettyPrint', 'quotaUser']

**And the required parameters**

.. code-block:: python3

    >>> list_url.required_parameters

    []

**Let's check out what the ``start_token`` optional parameter is and how it should look like**

.. code-block:: python3

    >>> list_url.parameters['start_token']

    {
        "type": "string",
        "description": "Token for requesting successive pages of results.",
        "location": "query"
    }


**Finally let's create a request, that we'll then send with Aiogoogle**

.. code-block:: python3

    >>> request = list_url(start_token='a_string', key='a_secret_key')

    # Equivalent to:

    >>> request = url_shortener.url.list(start_token='a_start_token', key='a_secret_key')

Here we passed the `url.list` method the parameters we want and an unsent request has been created

**We can inspect the URL of the request by typing:**

.. code-block:: python3

    >>> request.url
     
    'https://www.googleapis.com/url/history?start_token=a_start_token&key=a_secret_key'

Send a Request
------------------

**Let's create a coroutine that shortens URLs using an API key**

.. code-block:: python3

    import asyncio
    from aiogoogle import Aiogoogle
    from pprint import pprint

    api_key = 'you_api_key'

    async def shorten_urls(long_url):
        async with Aiogoogle(api_key=api_key) as google:
            url_shortener = await google.discover('urlshortener', 'v1')
            short_url = await google.as_api_key(
                url_shortener.url.insert(
                    json=dict(
                        longUrl=long_url
                    )
            )

        return short_url

    short_url = asyncio.run(shorten_urls('https://www.google.com'))
    pprint(short_url)

.. code-block:: python

    {
        "kind": "urlshortener#url",
        "id": "https://goo.gl/Dk2j",
        "longUrl": "https://www.google.com/"
    }

Send Requests Concurrently:
-------------------------------

**Now let's shorten two URLs at the same time**

.. code-block:: python

    import asyncio
    from aiogoogle import Aiogoogle
    from pprint import pprint

    async def shorten_url(long_urls):
        async with Aiogoogle(api_key=api_key) as google:
            url_shortener = await google.discover('urlshortener', 'v1')
            short_urls = await google.as_api_key(

                url_shortener.url.insert(
                    json=dict(
                        longUrl=long_url[0]
                    ),
                
                url_shortener.url.insert(
                    json=dict(
                        longUrl=long_url[1]
                    )
            )
        return short_urls

    short_urls = asyncio.run(
        shorten_url(
            ['https://www.google.com', 'https://www.google.org']
        )
    )
    pprint(short_urls)

.. code-block:: python

    [
        {
            "kind": "urlshortener#url",
            "id": "https://goo.gl/Dk2j",
            "longUrl": "https://www.google.com/"
        },
        {
            "kind": "urlshortener#url",
            "id": "https://goo.gl/Dk23",
            "longUrl": "https://www.google.org/"
        }
    ]


Send As Client
------------------

.. code-block:: python

    #!/usr/bin/python3.7

    import asyncio, pprint
    from aiogoogle import Aiogoogle

    api_key = 'abc123'

    async def translate_to_latin(words):
        async with Aiogoogle(api_key=api_key) as aiogoogle:
            language = await aiogoogle.discover('translate', 'v2')
            words = dict(q=[words], target='la')
            result = await aiogoogle.as_api_key(
                language.translations.translate(json=words)
            )
        pprint.pprint(result)

    if __name__ == '__main__':
        asyncio.run(translate_to_latin('Aiogoogle is awesome'))

.. code-block:: bash

    {
        "data": {
            "translations": [
                {
                    "translatedText": "Aiogoogle est terribilis!",  
                    # Google probably meant "awesomelis", but whatever..
                    "detectedSourceLanguage": "en"
                }
            ]
        }
    }

Send As User (`Authorization Code Flow`_)
--------------------------------------------------------

.. code-block:: python

    import asyncio
    from aiogoogle import Aiogoole
    from pprint import pprint

    USER_CREDS = {'access_token': '...'}

    async def get_calendar_events():
        async with Aiogoogle(user_creds=USER_CREDS) as aiogoogle:
            calendar_v3 = await aiogoogle.discover('calendar', 'v3')
            result = await aiogoogle.as_user(
                calendar_v3.events.list(
                    calendarId="primary",
                    maxResults=1
                )
            )
        pprint.pprint(result)

    asyncio.run(get_calendar_events())

.. code-block:: bash

    {
        "kind": "calendar#events",
        "etag": "\"p33c910kumb6ts0g\"",
        "summary": "user@gmail.com",
        "updated": "2018-11-11T22:31:03.463Z",
        "timeZone": "Africa/Cairo",
        "accessRole": "owner",
        "defaultReminders": [
            {
                "method": "popup",
                "minutes": 30
            },
            {
                "method": "email",
                "minutes": 30
            }
        ],
        "nextPageToken": "CigKGjVkcXIxa20wdHJrOW0xMXN0YABIAGNiQgp6yzd4C",
        "items": [
            {
                "kind": "calendar#event",
                "etag": "\"2784256013588000\"",
                "id": "asdasdasdasdasd",
                "status": "confirmed",
                "htmlLink": "https://www.google.com/calendar/event?eid=asdasdasdasdQG0",
                "created": "2014-02-11T14:13:26.000Z",
                "updated": "2014-02-11T14:13:26.794Z",
                "summary": "Do Something",
                "creator": {
                    "email": "omarryhan@gmail.com",
                    "displayName": "Omar Ryhan",
                    "self": true
                },
                "organizer": {
                    "email": "omarryhan@gmail.com",
                    "displayName": "Omar Ryhan",
                    "self": true
                },
                "start": {
                    "date": "2014-03-07"
                },
                "end": {
                    "date": "2014-03-08"
                },
                "iCalUID": "asdasdasd@google.com",
                "sequence": 0,
                "attendees": [
                    {
                        "email": "omarryhan@gmail.com",
                        "displayName": "Omar Ryhan",
                        "organizer": true,
                        "self": true,
                        "responseStatus": "accepted"
                    }
                ],
                "reminders": {
                    "useDefault": false,
                    "overrides": [
                        {
                            "method": "email",
                            "minutes": 450
                        },
                        {
                            "method": "popup",
                            "minutes": 30
                        }
                    ]
                }
            }
        ]
    }

Quick Examples
=================

List Files on Google Drive
---------------------------

.. code-block:: python3

    import asyncio
    from aiogoogle import Aiogoogle

    user_creds = {'access_token': 'an_access_token'}

    async def list_files():
        async with Aiogoogle(user_creds=user_creds) as aiogoogle:
            drive_v3 = await aiogoogle.discover('drive', 'v3')
            json_res = await aiogoogle.as_user(
                drive_v3.files.list(),
            )
            for file in json_res['files']:
                print(file['name'])

    asyncio.run(list_files())

Pagination
------------

.. code-block:: python3

    async def list_files():
        async with Aiogoogle(user_creds=user_creds) as aiogoogle:
            drive_v3 = await aiogoogle.discover('drive', 'v3')
            full_res = await aiogoogle.as_user(
                drive_v3.files.list(),
                full_res=True
            )
        async for page in full_res:
            for file in page['files']:
                print(file['name'])

    asyncio.run(list_files())

Download a File from Google Drive
----------------------------------

.. code-block:: python3

    async def download_file(file_id, path):
        async with Aiogoogle(user_creds=user_creds) as aiogoogle:
            drive_v3 = await aiogoogle.discover('drive', 'v3')
            await aiogoogle.as_user(
                drive_v3.files.get(fileId=file_id, download_file=path, alt='media'),
            )
    asyncio.run(download_file('abc123', '/home/user/Desktop/my_file.zip'))

Upload a File to Google Drive
--------------------------------

.. code-block:: python3

    async def upload_file(path):
        async with Aiogoogle(user_creds=user_creds) as aiogoogle:
            drive_v3 = await aiogoogle.discover('drive', 'v3')
            await aiogoogle.as_user(
                drive_v3.files.create(upload_file=path)
            )
    asyncio.run(upload_file('/home/aiogoogle/Documents/my_cool_gif.gif/'))

List Your Contacts
--------------------

.. code-block:: python3

    import asyncio

    async def list_contacts():
        aiogoogle = Aiogoogle(user_creds=user_creds)
        people_v1 = await aiogoogle.discover('people', 'v1')
        async with aiogoogle:
            contacts_book = await aiogoogle.as_user(
                people_v1.people.connections.list(
                    resourceName='people/me',
                    personFields='names,phoneNumbers'
                ),
                full_res=True
            )
        async for page in contacts_book:
            for connection in page['connections']:
                print(connection['names'])
                print(connection['phoneNumbers'])

    asyncio.run(list_contacts())

List Calendar Events
-----------------------

.. code-block:: python3

    async def list_events():
        async with Aiogoogle(user_creds=user_creds) as aiogoogle:
            calendar_v3 = await aiogoogle.discover('calendar', 'v3')
            res = await aiogoogle.as_user(
                calendar_v3.events.list(calendarId='primary')
            )
            pprint.pprint(res)

Check out https://github.com/omarryhan/aiogoogle/tree/master/examples for more.

Design
=======

Async framework agnostic
-------------------------

Aiogoogle does not and will not enforce the use of any async/await framework e.g. Asyncio, Curio or Trio. As a result, modules that handle *io* are made to be easily pluggable.

If you want to use Curio instead of Asyncio:

.. code-block:: bash

    pip install aiogoogle[curio_asks]

e.g.

.. code-block:: python3

    import curio

    from aiogoogle import Aiogoogle
    from aiogoogle.sessions.curio_asks_session import CurioAsksSession

    async def main():
        async with Aiogoogle(session_factory=CurioAsksSession) as google:
            youtube = await google.discover('youtube', 'v3')

    curio.run(main)

Another e.g.

.. code-block:: python3

    #!/usr/bin/python3.7

    import curio, pprint

    from aiogoogle import Aiogoogle
    from aiogoogle.sessions.curio_asks_session import CurioAsksSession

    async def list_events():
        async with Aiogoogle(user_creds=user_creds, client_creds=client_creds, session_factory=CurioAsksSession) as aiogoogle:
            calendar_v3 = await aiogoogle.discover('calendar', 'v3')
            events = await aiogoogle.as_user(
                calendar_v3.events.list(calendarId='primary'),
            )
        pprint.pprint(events)

    if __name__ == '__main__':
        curio.run(list_events)

The same with asyncio would look like this:

.. code-block:: python3

    #!/usr/bin/python3.7

    import asyncio, pprint

    from aiogoogle import Aiogoogle
    from aiogoogle.sessions.aiohttp_session import AiohttpSession  # Default

    async def list_events():
        async with Aiogoogle(user_creds=user_creds, client_creds=client_creds, session_factory=AiohttpSession) as aiogoogle:
            calendar_v3 = await aiogoogle.discover('calendar', 'v3')
            events = await aiogoogle.as_user(
                calendar_v3.events.list(calendarId='primary'),
            )
        pprint.pprint(events)

    if __name__ == '__main__':
        asyncio.run(list_events)


And Trio:

.. code-block:: bash

    pip install aiogoogle[trio_asks]

.. code-block:: python3

    #!/usr/bin/python3.7

    import trio, pprint

    from aiogoogle import Aiogoogle
    from aiogoogle.sessions.trio_asks_session import TrioAsksSession   # Default

    async def list_events():
        async with Aiogoogle(user_creds=user_creds, client_creds=client_creds, session_factory=TrioAsksSession) as aiogoogle:
            calendar_v3 = await aiogoogle.discover('calendar', 'v3')
            events = await aiogoogle.as_user(
                calendar_v3.events.list(calendarId='primary'),
            )
        pprint.pprint(events)

    if __name__ == '__main__':
        trio.run(list_events)

Lightweight and minimalistic 
------------------------------

Aiogoogle is built to be as lightweight and extensible as possible so that both client facing applications and API libraries can use it.



API
=====

Aiogoogle
----------

.. autoclass:: aiogoogle.client.Aiogoogle
    :members:
    :undoc-members:
    :show-inheritance:


GoogleAPI
----------

.. autoclass:: aiogoogle.resource.GoogleAPI
    :members:
    :undoc-members:
    :show-inheritance:

Resource
-----------

.. autoclass:: aiogoogle.resource.Resource
    :members:
    :undoc-members:
    :show-inheritance:

Method
---------

.. autoclass:: aiogoogle.resource.Method
    :members:
    :undoc-members:
    :show-inheritance:

Credentials
--------------

.. automodule:: aiogoogle.auth.creds
    :members:
    :undoc-members:
    :show-inheritance:

Auth Managers
--------------

.. automodule:: aiogoogle.auth.managers
    :members:
    :undoc-members:
    :show-inheritance:


Exceptions
-----------

.. automodule:: aiogoogle.excs
    :members:
    :undoc-members:
    :show-inheritance:


Models
---------

.. automodule:: aiogoogle.models
    :members:
    :undoc-members:
    :show-inheritance:


Utils
---------

.. automodule:: aiogoogle.utils
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: aiogoogle.auth.utils
    :members:
    :undoc-members:
    :show-inheritance:

Validate
----------

.. automodule:: aiogoogle.validate
    :members:
    :undoc-members:
    :show-inheritance:


Sessions
-----------

.. autoclass:: aiogoogle.sessions.aiohttp_session.AiohttpSession
    :show-inheritance:

.. autoclass:: aiogoogle.sessions.curio_asks_session.CurioAsksSession
    :show-inheritance:

.. autoclass:: aiogoogle.sessions.trio_asks_session.TrioAsksSession
    :show-inheritance:


Tips and hints
===============

1. For a more efficient use of your quota use `partial responses <https://developers.google.com/discovery/v1/performance#partial-response>`_.

Contribute 🙋
================

There's a bunch you can do to help regardless of your experience level:

1. Features, chores and bug reports:
    Please refer to the Github issue tracker where they are posted. 

2. Examples:
    You can add examples to the examples folder

3. Testing
    Add more tests, the library is currently a bit undertested

Take your pick :)

:ref:`genindex`
:ref:`modindex`
:ref:`search`

