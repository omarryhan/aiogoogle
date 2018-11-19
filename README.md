<p align="center">
  <img src="https://i2.wp.com/googlediscovery.com/wp-content/uploads/google-developers.png" alt="Logo" title="Aiogoogle" height="150" width="200"/>
  <p align="center">
    <a href="https://travis-ci.org/omarryhan/aiogoogle"><img alt="Build Status" src="https://travis-ci.org/omarryhan/aiogoogle.svg?branch=master"></a>
    <a href="https://github.com/omarryhan/aiogoogle"><img alt="Software License" src="https://img.shields.io/badge/license-GNU-brightgreen.svg?style=flat-square"></a>
  </p>
</p>

# Aiogoogle
### **Alpha**

## Usage

**1. Load Client:**

*From the discovery API:*

    from aiogoogle import DiscoveryClient

    client = DiscoveryClient()
    youtube = await client.discover('youtube', 'v3')

***Or** from a discovery document:*

    youtube = DiscoveryClient(discovery_document=dict_disc_doc)

**2. Set your credentials:**

*Set an API key:*

    youtube.api_key = 'api_key'

*Or, set Oauth2 Client Creds:*

    youtube.client_creds = {
      'client_id': 'a_client_id',
      'client_secret': 'a_client_secret',
      'redirect_uri': 'https://example.com/callback'
    }

*Or, Set Oauth2 User Creds:*

    youtube.user_creds = {
      'access_token': 'an_access_token_12345'
    }

**3. Send Requests:**

    result = await youtube.send_as_api_key(
      youtube.resources.videos.list(part='snippet')  # This line returns an unsent request object
    )

    results = await youtube.send_as_user_creds(
      youtube.resources.videos.list(part='snippet)
      youtube.resources.captions.download(id='12345', download_file='/home/user/captions.json, timeout=6)
    )

    result = await youtube.send_unauthorized(
      youtube.resources.videos.list(part='snippet')  # Raises AuthError
    )

**4. OAuth2:**

*I. OAuth2 Authorization Code Flow (Probably the one you'll need):*

1. Prepare authorization URI and wait for callback

        uri, user_creds = youtube.oauth2_manager.build_uri(client_creds)  # User creds stores a CSRF token but doesn't have an access token yet

2. Build user_creds with the grant code received in the callback

        user_creds = await youtube.oauth2_manager.build_user_creds(grant, client_creds, user_creds)

3. Set user_creds to client

        youtube.user_creds = user_creds

4. Now you can fetch resources with the user_creds you you have set and your OAuth2 manager will refresh your access token automatically

        results = await youtube.send_as_user(
            youtube.resources.videos.list(part='snippet')
        )

*II. OAuth2 Client Credentials Flow (Usually provides limited scope):*

1. Authorize using client credentials flow

        client_creds = dict(client_id='a_client_id', client_secret='a_client_secret')
        authorized_client_creds = youtube.oauth2_manager.build_client_creds(client_creds)

2. Set client_creds to client

        youtube.client_creds = authorized_client_creds

3. Call a resource with client_creds

        results = await youtube.send_as_client(
          youtube.resources.videos.list(part='snippet')
        )

## Please Note:

- This module will monkey patch some functions, methods and classes from the jsonschema package. If you're using the jsonschema package anywhere else in your code, then this library might cause you lots of trouble.

## API

    - DiscoveryClient

      # Keys
      - client_creds
      - user_creds
      - api_key

      # Auth Managers
      - Oauth2Manager
        - build_oauth2_uri
        - coro build_client_creds
        - coro build_user_creds

      # Send Requests
      - coro send_as_user
      - coro send_as_client
      - coro send_as_key

      # Misc
      - authorized_for_method

      # Resources
      - resources (Resource)

        - resource

          - method
            - __call__  --> Creates the request

          - resource (Resource) 

        - 

### Under Construction!
### Still alpha, API might break and expect it to be buggy.