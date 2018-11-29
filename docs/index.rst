.. Aiogoogle documentation master file, created by
   sphinx-quickstart on Tue Nov 20 20:02:59 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Aiogoogle
==========

An **Asynchronous** Discovery Service Client

Discovery Service?
==================

Most of Google's public APIs are served by a single API called the Discovery Service. e.g. (Youtube, Gmail, Google Analytics, Calendar etc.)

Google's Discovery Serivce provides machine readable specifications known as discovery documents. `e.g. Google Books <https://www.googleapis.com/discovery/v1/apis/books/v1/rest>`_.

In it's essence, Aiogoogle is a feature-rich yet easy to use Pythonic wrapper for discovery documents.

For a list of supported APIs, visit: `Google's APIs Explorer <https://developers.google.com/apis-explorer/>`_.


Library Setup
=============

.. code-block:: bash

    $ python3.7 -m pip install --user --upgrade aiogoogle

Google Account Setup
====================

1. **Create a project:** `Google's APIs and Services dashboard <https://console.cloud.google.com/projectselector/apis/dashboard>`_.
2. **Enable an API:** `API Library <https://console.cloud.google.com/apis/library>`_.
3. **Create credentials:** `Credenitals wizard <https://console.cloud.google.com/apis/credentials/wizard?>`_.
4. **Pick an API:** `Google's APIs Explorer <https://developers.google.com/apis-explorer/>`_ 

    .. note:: After choosing an API, get the API's *name* and *version* from the URL as they will be needed later.

Usage
========

Now that *Aiogoogle* and your Google account are set up, let's start!

Assuming you chose the Urlshortener-v1 API:

Create a Google API instance
--------------------------------

.. code-block:: python3

    import asyncio
    from aiogoogle import Aiogoogle

    async def create_api(name, version):

        async with Aiogoogle() as google:

            return await google.discover(name, version)

    url_shortener = asyncio.run(
        create_api('urlshortener', 'v1')
    )

    >>> url_shortener['resources']


.. code-block:: python3

    {
        'url': {

            'methods':

                'get': ...
                'insert': ...
                'list': ...
    }

Browse an API
-----------------

**Now, let's browse a resource**

.. code-block:: python3

    >>> url_resource = url_shortener.url

    >>> url_resource.methods

    ['get', 'insert', 'list']

**Sometimes resources have nested resources**

.. code-block:: python3

    >>> url_resource.resources

    []

**Let's inspect a method of a resource**

.. code-block:: python3

    >>> list_url = url_resource.list

    >>> list_url['description']

    "Retrieves a list of URLs shortened by a user."
    
    >>> list_url.optional_parameters

    ['projection', 'start_token', 'alt', 'fields', 'key', 'oauth_token', 'prettyPrint', 'quotaUser']

    >>> list_url.required_parameters

    []

**Let's check out what the ``start_token`` parameter is and how it should look like**

.. code-block:: python3

    >>> list_url.parameters['start_token']

    {
        "type": "string",
        "description": "Token for requesting successive pages of results.",
        "location": "query"
    }


**Finally let's create a request, that we'll then send with Aiogoogle**

.. code-block:: python3

    >>> request = list_url(start_token='a_string')

    # Equivalent to:

    >>> request = url_shortener.url.list(start_token='a_start_token', key='a_secret_key')

    >>> request.url
     
    'https://www.googleapis.com/url/history?start_token=a_start_token&key=a_secret_key'


Send a Request
------------------

**Let's create a coroutine that shortens URLs**

.. code-block:: python3

    import asyncio
    from aiogoogle import Aiogoogle
    from pprint import pprint

    async def shorten_urls(long_url):

        async with Aiogoogle() as google:

            url_shortener = await google.discover('urlshortener', 'v1')
        
            short_url = await google.as_anon(

                url_shortener.url.insert(longUrl=long_url)

            )

        return short_url

    short_url = asyncio.run(shorten_urls('https://www.example.com'))
    pprint(short_url)

.. code-block:: python

    {
        "kind": "urlshortener#url",
        "id": "https://goo.gl/Dk2j",
        "longUrl": "https://www.example.com/"
    }

Send Requests Concurrently:
-------------------------------

**Now let's shorten two URLs at the same time**

.. code-block:: python

    import asyncio
    from aiogoogle import Aiogoogle
    from pprint import pprint

    async def shorten_url(long_urls):

        async with Aiogoogle() as google:

            url_shortener = await google.discover('urlshortener', 'v1')
        
            short_urls = await google.as_anon(

                url_shortener.insert(longUrl=long_urls[0]),
                url_shortener.insert(longUrl=long_urls[1])

            )

        return short_urls

    short_urls = asyncio.run(
        shorten_url(
            ['https://www.example.com', 'https://www.example.org']
        )
    )
    pprint(short_urls)

.. code-block:: python

    [
        {
            "kind": "urlshortener#url",
            "id": "https://goo.gl/Dk2j",
            "longUrl": "https://www.example.com/"
        },
        {
            "kind": "urlshortener#url",
            "id": "https://goo.gl/Dk23",
            "longUrl": "https://www.example.org/"
        }
    ]


Send As Client
------------------

.. code-block:: python

    import asyncio
    from aiogoogle import Aiogoole
    from pprint import pprint

    API_KEY = 'get_away_eve_this_is_only_for_bob'

    async def translate_to_latin(words):

        async with Aiogoogle(api_key=API_KEY) as google:

            translator = await google.discover('translate', 'v2')
            
            words = dict(q=[words], target='la')

            result = await google.as_api_key(
                
                translator.translations.translate(json=words)

            )

        return result

    translation = asyncio.run(
        translate_to_latin('Googleaio is awesome!')
    )
    pprint(translation)

.. code-block:: bash

    {
        "data": {
            "translations": [
                {
                    "translatedText": "Googleaio est terribilis!",  
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

        async with Aiogoogle(user_creds=USER_CREDS) as google:

            calendar_v3 = await google.discover('calendar', 'v3')
            
            result = await google.as_user_creds(
                
                calendar_v3.calendar.events.list(
                    calendarId="primary",
                    maxResults=1
                )

            )

        return result

    user_events = asyncio.run(get_calendar_events())
    pprint(user_events)

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

Authorization and Authentication
================================

Most of Google's APIs that are supported by the discovery service support these 3 authentication/authorization schemes:

1. **OAuth2**

    Should be used whenever you want to access personal information.

2. **API key**

    Should be used when accessing Public information.
    
    A simple secret string, that you can get from Google's Cloud Console

    .. note::
        
        For most personal information, an API key won't be enough.

        You should use OAuth2 instead.

3. **Service Accounts**

    For bot to bot communication. `See here <https://cloud.google.com/iam/docs/overview>`_
    
    Useful if you run an application on any of Google Cloud Products.
    
    .. note::
        
        Not yet supported by Aiogoogle

OAuth2 Primer
--------------

Oauth2 serves as an authentication and authorization framework. It supports four main flows:

1. **Authorization code flow**:
    
    - Only one supported by aiogoogle
    - `RFC6749 section 4.1  <https://tools.ietf.org/html/rfc6749#section-4.1>`_.

2. **Client Credentials Flow**:

    - Similar to API_KEY authentication so use API key authentication instead
    - `RFC6749 section 4.4  <https://tools.ietf.org/html/rfc6749#section-4.4>`_.

3. **Implicit Grant Flow**:
    - Not supported  
    - `RFC6749 section 4.2  <https://tools.ietf.org/html/rfc6749#section-4.2>`_.

4. **Resource Owner Password Credenitals Flow**:
    
    - Not supported
    - `RFC6749 section 4.3  <https://tools.ietf.org/html/rfc6749#section-4.2>`_.

Since Aiogoogle only supports Authorization Code Flow, let's get a little in to it:

Authorization Code Flow
------------------------

There three main parties are involved in this flow:

1. **User**: 
    - represented as ``aiogoogle.user_creds``
2. **Client**:
    - represented as ``aiogoogle.client_creds``
    - 3rd party
3. **Resource Server**:
    - The service aiogoogle acts as a client to. e.g. Google Analytics, Youtube, etc. 

Here's a nice ASCII chart as shown in `RFC6749 section 4.1 Figure 3 <https://tools.ietf.org/html/rfc6749#section-4.1.1>`_.::

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


**Example with Sanic (An asynchronous web framework)**
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

Install sanic

.. code-block:: bash

    pip install --user --upgrade sanic

.. warning::

    Do not copy and paste the following snippet as is.

    The error and return messages shown below are very verbose and aren't fit for production.

.. hint:: Code reads from top to bottom

./app.py

.. code-block:: python3

    import webbrowser
    
    from sanic import Sanic, response
    from sanic.exceptions import ServerError
    from aiogoogle import Aiogoogle, GoogleAPI, AuthError, StateError

    CLIENT_CREDS = {
        'client_id': '...',
        'client_secret': '...',
        'scopes': ['...', '...'],
    }
    LOCAL_ADDRESS = 'localhost'
    LOCAL_PORT = '5000'
    LOCAL_FULL_ADDRESS = local_address + ':' + str(local_port)

    app = Sanic(__name__)
    aiogoogle = Aiogoogle(client_creds=CLIENT_CREDS)

    #----------------------------------------#
    #                                        #
    # **Step A (Check OAuth2 figure above)** #
    #                                        #
    #----------------------------------------#

    @app.route('/authorize')
    def authorize(request):
        if aiogoogle.oauth2_manager.is_oauth_ready(client_creds):

            # Create redirect uri + user_creds dict with a CSRF token
            uri, user_creds = aiogoogle.oauth2_manager.authorization_url(
                client_creds
            )

            # Save user creds to the current_user for
            # when they callback with a grant
            current_user.aiogoogle_creds = user_creds

            # Step A
            return response.redirect(uri)
        
        else:

            raise ServerError(
                'Client doesn't have enough info for Oauth2'
            )

    #----------------------------------------------#
    #                                              #
    # **Step B (Check OAuth2 figure above)**       #
    #                                              #
    #----------------------------------------------#
    #                                              #
    # NOTE:                                        #
    #     current_user should be authorizing       #
    #     your application right now.              #
    #                                              #
    #----------------------------------------------#

    #----------------------------------------------#
    #                                              #
    # **Step C, D & E (Check OAuth2 figure above)**#
    #                                              #
    #----------------------------------------------#

    # Step C  
    # Google should redirect current_user to
    # this endpoint with a grant code
    @app.route('/callback/yourapp')
    async def callback(request):

        # If error, return description
        if request.args.get('error'):
            return response.text('whoops!', 401)

        # If a grant code was returned
        elif request.args.get('code'):
            grant = request.args.get('code')
            state = request.args.get('state')
            user_creds = current_user.aiogoogle_creds

            # Fetch the rest of user_token info
            # (access token, refresh token, expiry etc..)
            # Step D & E (D sends grant code, E receives token info)
            try:
                full_user_creds = await aiogoogle.build_user_creds(
                    client_creds,
                    user_creds
                )

            # If states do not match, this error will be thrown
            except StateError:
                return response.text('NO!')

            # Shouldn't really happen since we actually
            # got a grant code back and it has been 
            # verified that it's our current_user who spawned it.
            # But hey, gotta handle them pesky errors!
            except AuthError:
                return response.text(
                    'Something went terribly wrong', 500
                )
            
            # If no errors were raised
            else:
                current_user.aiogoogle_creds = full_user_creds
                
                # <save_those_creds_to_db_or_file_of_choice>
                #
                # WARNING: Do not return an access token to the user, 
                #          it is to be solely used by the client.
                #
                # </save_those_creds_to_db_or_file_of_choice>
                
                return response.text('OK')

        else:
            # Should either receive a code or an error
            return response.text('Something's wrong with your callback')

    if __name__ == '__main__':
        webbrowser.open_new_tab(
            'http://' + local_full_address + '/authorize'
        )
        app.run(host=LOCAL_ADDRESS, port=str(LOCAL_PORT), debug=True)

Design
=======

Aiogoogle does not and will not enforce the use of any asynchronous framework e.g. Asyncio, Curio or Trio. As a result, modules that handle *io* are easily pluggable.

If you want to use Curio instead of Asyncio:

.. code-block:: bash

    pip install aiogoogle[curio-asks-session]

.. code-block:: python3

    import curio

    from aiogoogle import Aiogoogle
    from aiogoogle.sessions.curio_asks_session import CurioAsksSession

    async def main():
        async with Aiogoogle(session_factory=CurioAsksSession) as google:
            youtube = await google.discover('youtube', 'v3')

    curio.run(main)


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

Credenitals
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


More
=====

1. For a more efficient use of your quota use `partial responses <https://developers.google.com/discovery/v1/performance#partial-response>`_.
2. Discovery Document:
    
    One of the main objectives of this library is to act as a layer of abstraction over discovery documents.

    If you find any leaks in this abstraction and find yourself wanting to know more about the discovery document and how it's structured:

    then checkout `Overview of the discovery document <https://developers.google.com/discovery/v1/reference/apis>`_.



Contribute
===========

All contributions are welcome :)

Contributors
============

-


:ref:`genindex`
:ref:`modindex`
:ref:`search`

