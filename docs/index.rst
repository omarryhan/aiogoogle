.. Aiogoogle documentation master file, created by
   sphinx-quickstart on Tue Nov 20 20:02:59 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/github_64.png
   :align: right
   :scale: 100 %
   :target: https://github.com/omarryhan/aiogoogle

Aiogoogle
=================

**Async** Google API Client

Aiogoogle makes it possible to access most of Google's public APIs which include:

* Google Calendar API
* Google Drive API
* Google Contacts API
* Gmail API
* Google Maps API
* Youtube API
* Translate API
* Google Sheets API
* Google Docs API
* Gogle Analytics API
* Google Books API
* Google Fitness API
* Google Genomics API
* Google Cloud Storage
* Kubernetes Engine API
* And `more <https://developers.google.com/apis-explorer>`_.

Library Setup ⚙️
=====================

.. code-block:: bash

    $ pip install aiogoogle

Google Account Setup
===========================

1. **Create a project:** `Google's APIs and Services dashboard <https://console.cloud.google.com/projectselector/apis/dashboard>`_.
2. **Enable an API:** `API Library <https://console.cloud.google.com/apis/library>`_.
3. **Create credentials:** `Credentials wizard <https://console.cloud.google.com/apis/credentials/wizard?>`_.
4. **Pick an API:** `Google's APIs Explorer <https://developers.google.com/apis-explorer/>`_ 

Authentication
=====================

Google APIs can be called on behalf of 3 main principals:

1. **User account**
2. **Service account**
3. Anonymous principal by using: **API keys** 

User account
--------------

Should be used whenever the application wants to access information 
tied to a Google user.
Google provides two main authorization/authentication strategies that will 
enable your application act on behalf of a user account:

1. **OAuth2**
2. **OpenID Connect**

OAuth2
^^^^^^^^^^^^^

OAuth2 is an authorization framework used to allow a client (an app) to
act on behalf of a user. It isn't designed to identify who the user is,
rather only defines what a client (the app) can access.

OAuth2 has 4 main flows. The most popular of them and the only one supported by
Google is `Authorization Code Flow <https://tools.ietf.org/html/rfc6749#section-1.3.1>`_. 

There are **3** main parties involved in this flow:

1. **User**: 
    - represented as `UserCreds <index.html#aiogoogle.auth.creds.UserCreds>`__.
2. **Client**:
    - represented as `ClientCreds <index.html#aiogoogle.auth.creds.ClientCreds>`__.
3. **Resource Server/Authorization server**:
    - The service that aiogoogle acts as a client to. e.g. Calendar, Youtube, etc.

Quick auth script
""""""""""""""""""""

Here's a script that will help you get an access and refresh token for your personal Google account.

**Link**: https://github.com/omarryhan/aiogoogle/blob/master/examples/auth/oauth2.py

**Steps to run:**

* Clone the repo
* ``cd aiogoogle/examples``
* ``cp _keys.yaml keys.yaml``
* Fillout the following:
    - client_id
    - client_secret
    - scopes
* ``cd aiogoogle/examples/auth``
* run ``python oauth2.py``
* After the webbrowser opens and you authorize your app, a `UserCreds <index.html#aiogoogle.auth.creds.UserCreds>`__ JSON object will be returned to your browser.
* Copy the access token and refresh token and either paste them in keys.yaml if you'll be using the examples directory. Or copy and paste them in your own code.

Integrate OAuth2 in an existing web app
"""""""""""""""""""""""""""""""""""""""""""

If you want to integrate OAuth2 in an existing web app, or use it on many users (not just your personal account), then follow these steps:

1. Generate an authentication URL and send it to the user you wish to access their data on their behalf.

.. code-block:: python3

    @app.route('/authorize')
    def authorize(request):
        uri = aiogoogle.auth.managers.Oauth2Manager().authorization_url(
            client_creds={
                'client_id': '...',
                'client_secret': '...',
                'scopes': [
                    '...',
                    '...'
                ],
                'redirect_uri': 'http://localhost:5000/callback/aiogoogle'
            },
        )
        return response.redirect(uri)

2. Now, the user should get redirected to Google's auth webpage, were they will be prompted to give your app the authorization it requested.

3. After the user authorizes your app, the user should get redirected back to your domain (to the ``redirect_uri`` you specified in step 1) giving you a grant code (not to be confused with an access token). Using this grant code, your application should then request a `UserCreds <index.html#aiogoogle.auth.creds.UserCreds>`__ dict which will contain an access and a refresh token.

.. code-block:: python3

    @app.route('/callback/aiogoogle')
    async def callback(request):
        # First, check if there's an error
        if request.args.get('error'):
            error = {
                'error': request.args.get('error'),
                'error_description': request.args.get('error_description')
            }
            return response.json(error)

        # Here we request the access and refresh token
        elif request.args.get('code'):
            full_user_creds = await aiogoogle.auth.managers.Oauth2Manager().build_user_creds(
                grant = request.args.get('code'),
                client_creds = CLIENT_CREDS
            )
            # Here, you should store full_user_creds in a db. Especially the refresh token and access token. 
            return response.json(full_user_creds)

        else:
            # Should either receive a code or an error
            return response.text("Something's probably wrong with your callback")

.. warning::

    You shouldn't hand the user of your app their access and refresh tokens.

    This is only done here for convenience and for personal use.

    Ideally, you'd want to store their tokens in a database on your backend.

OpenID Connect
^^^^^^^^^^^^^^^^^^^

OpenID Connect is an authentication layer built on top of OAuth2 
(an authorization framework). This method should be used when the client 
(the app) wants to identify the user i.e. authenticate them.
Since OpenID connect is a superset of OAuth2, this method will 
also give the client the authorization needed to edit resources of the user.

In more practical terms, using OAuth2 alone will only return you a token 
that can be used to access the data with the scope that the app requested. 
Using OpenIDConnect will return the same access token as with OAuth2 **plus**
an ID token JWT of the user. This ID token JWT will 
contain "claims" about the user which your app will need to properly know who they are. Here's
an `example <https://developers.google.com/identity/protocols/oauth2/openid-connect#an-id-tokens-payload>`__ of
how an ID token JWT should look like.

.. hint:: OpenID Connect should be used if you're implementing "social signin".

Quick auth script
"""""""""""""""""""

Here's a script that can help you get an access & refresh token + OpenID connect claims for your personal Google account.

**Link:** https://github.com/omarryhan/aiogoogle/blob/master/examples/auth/openid_connect.py

**Steps to run:**

* Clone the repo
* ``cd aiogoogle/examples``
* ``cp _keys.yaml keys.yaml``
* Fillout the following:
    - client_id
    - client_secret
    - scopes
* ``cd aiogoogle/examples/auth``
* run ``python openid_connect.py``
* After the webbrowser opens and you authorize your app, a `UserCreds <index.html#aiogoogle.auth.creds.UserCreds>`__ JSON object and a `User Info <https://developers.google.com/identity/protocols/oauth2/openid-connect#an-id-tokens-payload>`_ JSON object will be returned to your browser.
* Copy the access token and refresh token and either paste them in keys.yaml if you'll be using the examples directory. Or copy and paste them in your own code.

Integrate OpenID Connect in an existing web app
""""""""""""""""""""""""""""""""""""""""""""""""""""""

This works just like OAuth2 but with a few differences.

As before, we first redirect the user to the authorization prompt page.

.. code-block:: python3

    @app.route('/authorize')
    def authorize(request):
        uri = aiogoogle.openid_connect.authorization_url(
            client_creds={
                'client_id': '...',
                'client_secret': '...',
                'redirect_uri': '...',
                'scopes': [
                    '...'
                ]
            },
            nonce='...'  # Random value that prevents replay attacks
        )
        return response.redirect(uri)

After the user authorizes your app and gets redirected back to your domain, you should then request the access and refresh token.

The difference here is that aside from the `full_user_creds <index.html#aiogoogle.auth.creds.UserCreds>`__ dict, you also get the `full_user_info <https://developers.google.com/identity/protocols/oauth2/openid-connect#an-id-tokens-payload>`_ dict. This dict has claims about the user. Here's an example ``full_user_info`` dict:

.. code-block:: json

    {
        "iss": "https://accounts.google.com",
        "azp": "1234987819200.apps.googleusercontent.com",
        "aud": "1234987819200.apps.googleusercontent.com",
        "sub": "10769150350006150715113082367",
        "at_hash": "HK6E_P6Dh8Y93mRNtsDB1Q",
        "hd": "example.com",
        "email": "jsmith@example.com",
        "email_verified": "true",
        "iat": 1353601026,
        "exp": 1353604926,
        "nonce": "0394852-3190485-2490358"
    }

You should use the ``sub`` claim to uniquely identify your user. Google guarantees that this claim will be unique, unlike the email (common mistake).

If you want to understand what the rest of the claims are used for, please head `here <https://developers.google.com/identity/protocols/oauth2/openid-connect#an-id-tokens-payload>`__.

.. code-block:: python3

    @app.route('/callback/aiogoogle')
    async def callback(request):
        if request.args.get('error'):
            error = {
                'error': request.args.get('error'),
                'error_description': request.args.get('error_description')
            }
            return response.json(error)

        elif request.args.get('code'):
            # Returns an access and refresh token
            full_user_creds = await aiogoogle.openid_connect.build_user_creds(
                grant=request.args.get('code'),
                client_creds=CLIENT_CREDS,
                nonce=nonce,  # Same nonce as above
                verify=False
            )

            # A dict having claims of the user e.g. the sub claim and iat claim.
            # Check https://developers.google.com/identity/protocols/oauth2/openid-connect#an-id-tokens-payload for more info
            full_user_info = await aiogoogle.openid_connect.get_user_info(full_user_creds)

            # Here you should save both full_user_creds and full_user_info to a db if your app will be serving multiple users.
            return response.text(
                f"full_user_creds: {pprint.pformat(full_user_creds)}\n\nfull_user_info: {pprint.pformat(full_user_info)}"
            )

        else:
            # Should either receive a code or an error
            return response.text("Something's probably wrong with your callback")

.. warning::

    You should neither hand the user of your app their tokens nor their OpenID Connect claims.

    This is only done here for convenience and for personal use.

    Ideally, you'd want to store their info in a database on your backend.

Service account
-----------------------------

A service account is a special kind of account that belongs to an application
or a virtual machine (VM) instance but not a person. 
They are intended for scenarios where your application needs to
access resources or perform actions on its own, 
such as running App Engine apps or interacting with Compute Engine instances.

There are a couple of authentication/authorization methods you 
can use with service accounts. We'll only concern ourselves with
the ones that will grant us access to Google APIs and not for
any other purpose e.g. communicating with other servers on a different cloud,
as this is out of scope.

OAuth2
^^^^^^^^^^^^^

OAuth2 is the most commonly used service account authorization method and the only one implemented by Aiogoogle.
There are a couple of ways you can access Google APIs using OAuth2 
tokens for service accounts:

**1. By passing a user managed service account key:**

Full example `here <https://github.com/omarryhan/aiogoogle/blob/master/examples/list_storage_buckets.py>`__.

.. code-block:: python3

    import json
    import asyncio
    from aiogoogle import Aiogoogle
    from aiogoogle.auth.creds import ServiceAccountCreds


    service_account_key = json.load(open('test_service_account.json'))

    creds = ServiceAccountCreds(
        scopes=[
            "https://www.googleapis.com/auth/devstorage.read_only",
            "https://www.googleapis.com/auth/devstorage.read_write",
            "https://www.googleapis.com/auth/devstorage.full_control",
            "https://www.googleapis.com/auth/cloud-platform.read-only",
            "https://www.googleapis.com/auth/cloud-platform",
        ],
        **service_account_key
    )


    async def list_storage_buckets(project_id=creds["project_id"]):
        async with Aiogoogle(service_account_creds=creds) as aiogoogle:
            storage = await aiogoogle.discover("storage", "v1")
            res = await aiogoogle.as_service_account(
                storage.buckets.list(project=creds["project_id"])
            )
            print(res)


    if __name__ == "__main__":
        asyncio.run(list_storage_buckets())


**2. By pointing the** ``GOOGLE_APPLICATION_CREDENTIALS`` **environment variable at the location of the JSON key file.**

Full example `here <https://github.com/omarryhan/aiogoogle/blob/master/examples/list_storage_buckets_detect_default.py>`__.

First, set the environment variable, if not already set:

.. code-block:: sh

    export GOOGLE_APPLICATION_CREDENTIALS="location_of_key_file.json"

Then:

.. code-block:: python3

    import asyncio
    import print
    from aiogoogle import Aiogoogle
    from aiogoogle.auth.creds import ServiceAccountCreds

    creds = ServiceAccountCreds(
        scopes=[
            "https://www.googleapis.com/auth/devstorage.read_only",
            "https://www.googleapis.com/auth/devstorage.read_write",
            "https://www.googleapis.com/auth/devstorage.full_control",
            "https://www.googleapis.com/auth/cloud-platform.read-only",
            "https://www.googleapis.com/auth/cloud-platform",
        ],
    )


    async def list_storage_buckets(project_id=creds["project_id"]):
        aiogoogle = Aiogoogle(service_account_creds=creds)

        # Notice this line. Here, Aiogoogle loads the service account key.
        await aiogoogle.service_account_manager.detect_default_creds_source()

        async with aiogoogle:
            storage = await aiogoogle.discover("storage", "v1")
            res = await aiogoogle.as_service_account(
                storage.buckets.list(project=creds["project_id"])
            )

        print(res)

    if __name__ == "__main__":
        asyncio.run(list_storage_buckets())


**3. Automatic detection from Google Cloud SDK (Not supported yet):**

This should call the Google Cloud SDK CLI and ask it for an access
token without passing ``service_account_creds``.

**4. Automatic detection from Google App Engine environment (Not supported yet):**

This should return an OAuth2 token for the service account and cache
it for the App Engine application without passing ``service_account_creds``.

**5. Automatic detection from Google Compute Engine/Google Cloud Run/Google Cloud Functions environment**

This should return an OAuth2 token from the Google Compute Engine metadata server, which means that you don't have to pass ``service_account_creds``, unless you want to specify scopes.

This should work the same as #2, but skip the part were you set the environment variable.

Full example `here <https://github.com/omarryhan/aiogoogle/blob/master/examples/list_storage_buckets_detect_default.py>`__.

Others
^^^^^^^

Other than the OAuth2 method, there are:

- OpenID connect ID token (OIDC ID token)
- Self-signed JWT credentials
- Self-signed On-demand JWT credentials
- `Short lived tokens <https://cloud.google.com/iam/docs/creating-short-lived-service-account-credentials>`_.

But they are not supported and you might want to consider another library if you want to use them.

Anonymous principal (API keys)
---------------------------------

An API key is a simple string that you can get from Google Cloud Console.

Using an API key is suitable for when you only want to access public data.

**Example:**

.. code-block:: python3

    async with Aiogoogle(api_key='...') as aiogoogle:
        google_api = await aiogoogle.discover('google_api', 'v1')
        result = await aiogoogle.as_api_key(
            google_api.foo.bar(baz='foo')
        )

Discovery Service
=======================

Most of Google's public APIs are documented/discoverable by a single API called the Discovery Service.

Google's Discovery Serivce provides machine readable specifications known as discovery documents 
(similar to `Swagger/OpenAPI <https://github.com/OAI/OpenAPI-Specification/blob/master/examples/v3.0/petstore.yaml>`_). `e.g. Google Books <https://www.googleapis.com/discovery/v1/apis/books/v1/rest>`_.

``Aiogoogle`` is a Pythonic wrapper for discovery documents.

For a list of supported APIs, visit: `Google's APIs Explorer <https://developers.google.com/apis-explorer/>`_.

Discovery docs and the ``Aiogoogle`` object explained
=========================================================

Intro
----------

Now that you have figured out which authentication scheme you are going to use and got your hands on an access and a refresh token, let's make some API calls.

Assuming that you chose the: *urlshortener v1* API:

.. note::

    As of March 30, 2019, the Google URL shortening service was shut down. So this only serves as an example.

**Create a URL-shortener Google API instance**

Let's discover the `urlshortener` discovery document and create an Aiogoogle representation of it and call it ``url_shortener``

.. code-block:: python3

    import asyncio
    from aiogoogle import Aiogoogle

    async def create_api(name, version):
        async with Aiogoogle(
            user_creds={'access_token': '...', 'refresh_token': '...'}  # Or use the UserCreds object. Same thing.
        ) as aiogoogle:
            # Downloads the API specs and creates an API object
            return await aiogoogle.discover(name, version)

    url_shortener = asyncio.run(
        create_api('urlshortener', 'v1')
    )

Structure of an API
---------------------------

This is what the JSON representation of the discovery document we downloaded looks like.

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

You don't have to worry about most of this. 
What's important to understand right now is that a discovery service is just a way to specify the **resources** and **methods** of an API.

**What are resources and methods?**

It's easier to explain this with an example.
In the youtube-v3 API, a **resource** can be: ``videos`` and a **method** would be: ``list``.

The way you would access the ``list`` method is by typing: ``youtube_v3.videos.list()``

**Some rules:**

A resource can also have nested resources. e.g. ``youtube_v3.videos.comments.list()``

There can be top level methods that are not associated with any resource. However, that's not common.

Finally, the only way you can get data from a Google API is by calling a method. You can't call a resource and expect data.

Next, we will programatically browse an API

Browse an API - Programatically
-----------------------------------

Back to the URL shortener API.

Let's list the resources of the URL shortener API

.. code-block:: python3

    >>> url_shortener['resources']

    {
        'url': {

            'methods':

                'get': ...
                'insert': ...
                'list': ...
    }


Now, let's browse the resource called ``url``

.. code-block:: python3

    >>> url_resource = url_shortener.url

    >>> url_resource.methods_available

It has the following methods available to call:

.. code-block:: python3

    ['get', 'insert', 'list']

Sometimes resources have nested resources

.. code-block:: python3

    >>> url_resource.resources_available

    []

This one doesn't.

Let's inspect the method called ``list`` of the ``url`` resource

.. code-block:: python3

    >>> list_url = url_resource.list

Let's see what this method does

.. code-block:: python3

    >>> list_url['description']

    "Retrieves a list of URLs shortened by a user."
    
Cool, now let's see the optional parameters that this method accepts

.. code-block:: python3

    >>> list_url.optional_parameters

    ['projection', 'start_token', 'alt', 'fields', 'key', 'oauth_token', 'prettyPrint', 'quotaUser']

And the required parameters

.. code-block:: python3

    >>> list_url.required_parameters

    []

Let's check out what the ``start_token`` optional parameter is and how it should look like

.. code-block:: python3

    >>> list_url.parameters['start_token']

    {
        "type": "string",
        "description": "Token for requesting successive pages of results.",
        "location": "query"
    }


Finally let's create a request, that we'll then send with Aiogoogle

.. code-block:: python3

    >>> request = list_url(start_token='a_string', key='a_secret_key')

    # Equivalent to:

    >>> request = url_shortener.url.list(start_token='a_start_token', key='a_secret_key')

Here we passed the ``url.list`` method the parameters we want and an unsent request has been created

We can inspect the URL of the request by typing:

.. code-block:: python3

    >>> request.url
     
    'https://www.googleapis.com/url/history?start_token=a_start_token&key=a_secret_key'

Browse an API - Manually
-----------------------------------

Sometimes it's easier to browse a discovery document manually instead of doing it through a Python terminal. Here's how to do it:

1. Download a JSON viewer on your browser of choice. e.g:

    https://chrome.google.com/webstore/detail/json-viewer/gbmdgpbipfallnflgajpaliibnhdgobh?hl=en-US

2. Put your API name and version in this link and open the link in your browser:

    https://www.googleapis.com/discovery/v1/apis/{api}/{version}/rest

    e.g.
    
    https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest

3. You'll then get a human readable JSON document with a structure similar to the one you've seen `above <https://aiogoogle.readthedocs.io/en/latest/#structure-of-an-api>`_.

Let's try to get a Youtube video rating using the "youtube-v3" api:

1. Expand the ``resources`` property
2. Expand the ``videos`` property (Which is a resource)
3. Expand the ``methods`` property to see what methods this resource has
4. Expand the ``getRating`` property (a method)
5. Expand the ``parameters`` property to see the arguments that this method accepts
6. Expand the ``id`` property (a parameter) which happens to be the only parameter being accepted
7. Read the ``required`` property to see whether or not this property is required
8. Read the ``type`` property to see the type of this parameter
9. Now to create an **unsent** request using this method, you can type: ``youtube_v3.videos.getRating(id='an_id')``

I hope you spot the pattern by now :)

Next we'll be sending all the unsent requests that we've been creating.


Send a Request
------------------

**Let's create a coroutine that shortens URLs using an API key**

When creating an Aiogoogle object, it defaults to using an `Aiohttp <https://github.com/aio-libs/aiohttp/>`_ session to send your requests with. More on changing the default session in `this <https://aiogoogle.readthedocs.io/en/latest/#async-framework-agnostic>`_ section.

.. code-block:: python3

    import asyncio
    from aiogoogle import Aiogoogle
    from pprint import pprint

    api_key = 'you_api_key'

    async def shorten_urls(long_url):
        async with Aiogoogle(api_key=api_key) as aiogoogle:
            url_shortener = await aiogoogle.discover('urlshortener', 'v1')
            short_url = await aiogoogle.as_api_key(  # the request is being sent here
                url_shortener.url.insert(
                    json=dict(
                        longUrl=long_url
                    )
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

Send Requests Concurrently
-------------------------------

**Now let's shorten two URLs at the same time**

.. code-block:: python

    import asyncio
    from aiogoogle import Aiogoogle
    from pprint import pprint

    async def shorten_url(long_urls):
        async with Aiogoogle(api_key=api_key) as aiogoogle:
            url_shortener = await aiogoogle.discover('urlshortener', 'v1')
            short_urls = await aiogoogle.as_api_key(

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


Send As API key
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

Send As User
----------------------

.. code-block:: python

    import asyncio
    from aiogoogle import Aiogoole
    from pprint import pprint

    async def get_calendar_events():
        async with Aiogoogle(user_creds={'access_token': '...', 'refresh_token': '...'}) as aiogoogle:
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

Examples
=================

You can find all examples in this `directory <https://github.com/omarryhan/aiogoogle/tree/master/examples>`_. Some of them are listed here for convenience.

List Files on Google Drive
---------------------------

Full example `here <https://github.com/omarryhan/aiogoogle/blob/master/examples/list_drive_files.py>`__.

.. code-block:: python3

    import asyncio
    from aiogoogle import Aiogoogle

    user_creds = {'access_token': '...', 'refresh_token': '...'}

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
	
Upload a File to Google Drive using an AsyncIterable
-----------------------------------------------------

Full example `here <https://github.com/omarryhan/aiogoogle/blob/master/examples/stream_upload_asynciterable.py>`__.

.. code-block:: python3
	async def yield_file():
		chunks = ['chunk1', 'chunk2']
		for chunk in chunks:
			yield chunk
			
    async def upload_iterable(iterable):
        async with Aiogoogle(user_creds=user_creds) as aiogoogle:
            drive_v3 = await aiogoogle.discover('drive', 'v3')
            await aiogoogle.as_user(
                drive_v3.files.create(pipe_from=iterable)
            )
    asyncio.run(upload_file(yield_file()))

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

Verify an Android In App Purchase
------------------------

We disable ``raise_for_status`` here, to prevent raising an HTTP error on invalid purchases.

.. code-block:: python3

   async def verify_purchase(token, package_name, product_id):
       async with Aiogoogle(
               service_account_creds=creds
       ) as aiogoogle:
           publisher_api = await aiogoogle.discover('androidpublisher', 'v3')

           request = publisher_api.purchases.products.get(
               token=token,
               productId=product_id,
               packageName=package_name)

           validation_result = await aiogoogle.as_service_account(
               request,
               full_res=True,
               raise_for_status=False
           )
       pprint(validation_result.content)

Check out https://github.com/omarryhan/aiogoogle/tree/master/examples for more.

Design and goals
===================

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
        async with Aiogoogle(session_factory=CurioAsksSession) as aiogoogle:
            youtube = await aiogoogle.discover('youtube', 'v3')

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

1. **Features, chores and bug reports:**

    Please refer to the Github issue tracker where they are posted. 

2. **Examples:**

    You can add examples to the examples folder

3. **Testing:**

    Add more tests, the library is currently a bit undertested

Take your pick :)

Development notes
=====================

To run the test suite
-------------------------

1. Install `tox <https://tox.wiki/en/latest/>`_
2. Run ``$ tox`` in the root of the project.
3. For extra configs, check out the tox.ini file.


To upload a new version
-------------------------

**Bump the version**

In: ``aiogoogle/__version__.py``

**Push a new tag**

Make a new Git tag then push it.

.. code-block:: sh

    $ git tag -a 1.0.1 -m "New version :tada:" master
    $ git push --tags

**Publish release**

Then go to Github -> Releases -> Click on the tag -> Write a release title and description -> Hit the publish release button.

The ``publish.yml`` Github action should take it from there.
It will build and then upload the new package to Pypi.

To install the local version of the aiogoogle instead of the latest one on Pip
--------------------------------------------------------------------------------

.. code-block:: sh

    $ pip uninstall aiogoogle
    $ cd {cloned_aiogoogle_repo_with_your_local_changes}
    $ pip install -e .

Now you can import aiogoogle from anywhere in your FS and make it use your local version

.. toctree::
    :hidden:

    index
