from abc import ABC, abstractmethod
import inspect

from ..models import Request


class AbstractOAuth2Manager(ABC):
    """
    OAuth2 manager that only supports Authorization Code Flow (https://tools.ietf.org/html/rfc6749#section-1.3.1)

    Arguments:

        session_factory (aiogoogle.sessions.AbstractSession): A session implementation

        verify (bool): whether or not to verify tokens fetched
    
    Note:
    
        For a flow similar to Client Credentials Flow (https://tools.ietf.org/html/rfc6749#section-1.3.4) use an ``api_key``
    """

    def __new__(cls, *args, **kwargs):
        # Get all coros of this the abstract class
        parent_abstract_coros = inspect.getmembers(
            AbstractOAuth2Manager, predicate=inspect.iscoroutinefunction
        )

        # Ensure all relevant child methods are implemented as coros
        for coro in parent_abstract_coros:
            coro_name = coro[0]
            child_method = getattr(cls, coro_name)
            if not inspect.iscoroutinefunction(child_method):
                raise RuntimeError(f"{child_method} must be a coroutine")

        # Resume with normal behavior of a Python constructor
        return super(AbstractOAuth2Manager, cls).__new__(cls)

    @abstractmethod
    def __init__(self, session_factory):
        raise NotImplementedError

    @abstractmethod
    def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    def __aexit__(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def authorize(self, request, user_creds) -> Request:
        """
        Adds OAuth2 authorization headers to requests given user creds

        Arguments:

            request (aiogoogle.models.Request):

                Request to authorize

            user_creds (aiogoogle.auth.creds.UserCreds):

                user_creds to refresh with

        Returns:

            aiogoogle.models.Request: Request with OAuth2 authorization header
        """
        raise NotImplementedError

    @abstractmethod
    def authorization_url(
        self,
        client_creds=None,
        state=None,
        access_type=None,
        include_granted_scopes=None,
        login_hint=None,
        prompt=None,
        response_type=None,
        scopes=None,
    ) -> str:
        """ 
        First step of OAuth2 authoriztion code flow. Creates an OAuth2 authorization URI.

        Arguments:

            client_creds (aiogoogle.auth.creds.ClientCreds):  A client_creds object/dictionary containing the following items:

                * client_id

                * scopes

                * redirect_uri

            scopes (list): List of OAuth2 scopes to ask for

                * Optional

                * Overrides the list of scopes specified in client creds
            
            state (str): A CSRF token

                * Optional

                * Specifies any string value that your application uses to maintain state between your authorization request and the authorization server's response.
                
                * The server returns the exact value that you send as a name=value pair in the hash (#) fragment of the redirect_uri after the user consents to or denies your application's access request.

                * You can use this parameter for several purposes, such as:
                
                    * Directing the user to the correct resource in your application
                    
                    * Sending nonces
                    
                    * Mitigating cross-site request forgery.

                * If no state is passed, this method will generate and add a secret token to ``user_creds['state']``.
                    
                * Since your redirect_uri can be guessed, using a state value can increase your assurance that an incoming connection is the result of an authentication request.
                
                * If you generate a random string or encode the hash of a cookie or another value that captures the client's state, you can validate the response to additionally ensure that the request and response originated in the same browser, providing protection against attacks such as cross-site request forgery.

            access_type (str): Indicates whether your application can refresh access tokens when the user is not present at the browser. Options:

                * Optional

                * ``"online"`` *Default*

                * ``"offline"`` Choose this for a refresheable/long-term access token

            include_granted_scopes (bool):
            
                * Optional

                * Enables applications to use incremental authorization to request access to additional scopes in context.
                
                * If you set this parameter's value to ``True`` and the authorization request is granted, then the new access token will also cover any scopes to which the user previously granted the application access.

            login_hint (str):
            
                * Optional
                
                * If your application knows which user is trying to authenticate, it can use this parameter to provide a hint to the Google Authentication Server.
                
                * The server uses the hint to simplify the login flow either by prefilling the email field in the sign-in form or by selecting the appropriate multi-login session.

                * Set the parameter value to an email address or sub identifier, which is equivalent to the user's Google ID.
                
                * This can help you avoid problems that occur if your app logs in the wrong user account.

            prompt (str):

                * Optional
                
                * A space-delimited, case-sensitive list of prompts to present the user.
                
                * If you don't specify this parameter, the user will be prompted only the first time your app requests access.
                
                * Possible values are:

                    * ``None`` : Default: Do not display any authentication or consent screens. Must not be specified with other values.

                    * ``'consent'`` : Prompt the user for consent.

                    * ``'select_account'`` : Prompt the user to select an account.

            response_type (str):

                * OAuth2 response type

                * Defaults to Authorization Code Flow response type

        Note:

            * It is highly recommended that you don't leave ``state`` as ``None`` in production.

            * To effortlessly create a random secret to pass it as a state token, you can use ``aiogoogle.auth.utils.create_secret()``

        Note:

            A Note About Scopes:

            * For a list of all of Google's available scopes: https://developers.google.com/identity/protocols/googlescopes

            * It is recommended that your application requests access to authorization scopes in context whenever possible.
            
            * By requesting access to user data in context, via incremental authorization, you help users to more easily understand why your application needs the access it is requesting.

        Warning:

            * When listening for a callback after redirecting a user to the URL returned from this method, take the following into consideration:
            
                * If your response endpoint renders an HTML page, any resources on that page will be able to see the authorization code in the URL.
                
                * Scripts can read the URL directly, and the URL in the Referer HTTP header may be sent to any or all resources on the page.

                * Carefully consider whether you want to send authorization credentials to all resources on that page (especially third-party scripts such as social plugins and analytics).
                
                * To avoid this issue, it's recommend that the server first handle the request, then redirect to another URL that doesn't include the response parameters.

        Example:

            ::

                from aiogoogle.auth.utils import create_secret
                from aiogoogle import ClinetCreds

                client_creds = ClientCreds(
                    client_id='a_client_id',
                    scopes=['first.scope', 'second.scope'],
                    redirect_uri='http://localhost:8080'
                )

                state = create_secret()

                auth_uri = oauth2.authorization_url(
                    client_creds=client_creds,
                    state=state,
                    access_type='offline',
                    include_granted_scopes=True,
                    login_hint='example@gmail.com',
                    prompt='select_account'
                    )

        Returns:

            (str): An Authorization URI
        """
        raise NotImplementedError

    @abstractmethod
    async def build_user_creds(self, grant, client_creds, grant_type=None):
        """
        Second step of Oauth2 authrization code flow. Creates a User Creds object with access and refresh token

        Arguments:

            grant (str):
            
                * Aka: "code". 
                
                * The code received at your redirect URI from the auth callback

            client_creds (aiogoogle.auth.creds.ClientCreds):

                * Dict with client_id and client_secret items

            grant_type (str):

                * OAuth2 grant type

                * defaults to ``code`` (Authorization code flow)

        Returns:

            aiogoogle.auth.creds.UserCreds: User Credentials with the following items:

                * ``access_token``

                * ``refresh_token``

                * ``expires_in`` (JSON format ISO 8601)

                * ``token_type`` always set to bearer

                * ``scopes``

        Raises:

            aiogoogle.excs.AuthError: Auth Error
        """
        raise NotImplementedError

    @abstractmethod
    def is_expired(self, user_creds):
        """
        Checks if user_creds expired

        Arguments:
        
            user_creds (aiogoogle.auth.creds.UserCreds): User Credentials

        Returns:

            bool:

        """
        raise NotImplementedError

    @abstractmethod
    async def refresh(self, user_creds, client_creds):
        """
        Refreshes user_creds
        
        Arguments:

            user_creds (aiogoogle.auth.creds.UserCreds): User Credentials with ``refresh_token`` item

            client_creds (aiogoogle.auth.creds.ClientCreds): Client Credentials

        Returns:

            aiogoogle.creds.UserCreds: Refreshed user credentials

        Raises:

            aiogoogle.excs.AuthError: Auth Error
        """
        raise NotImplementedError

    @abstractmethod
    async def revoke(self, user_creds):
        """
        Revokes user_creds

        In some cases a user may wish to revoke access given to an application. A user can revoke access by visiting Account Settings.
        It is also possible for an application to programmatically revoke the access given to it.
        Programmatic revocation is important in instances where a user unsubscribes or removes an application.
        In other words, part of the removal process can include an API request to ensure the permissions granted to the application are removed.

        Arguments:

            user_creds (aiogoogle.auth.Creds): UserCreds with an ``access_token`` item

        Returns:

            None:

        Raises:

            aiogoogle.excs.AuthError:
        """
        raise NotImplementedError


class AbstractOpenIdConnectManager(AbstractOAuth2Manager):
    def __new__(cls, *args, **kwargs):
        # Get all coros of this the abstract class
        parent_abstract_coros = inspect.getmembers(
            AbstractOpenIdConnectManager, predicate=inspect.iscoroutinefunction
        )

        # Ensure all relevant child methods are implemented as coros
        for coro in parent_abstract_coros:
            coro_name = coro[0]
            child_method = getattr(cls, coro_name)
            if not inspect.iscoroutinefunction(child_method):
                raise RuntimeError(f"{child_method} must be a coroutine")

        # Resume with normal behavior of a Python constructor
        return super(AbstractOpenIdConnectManager, cls).__new__(cls)

    @abstractmethod
    def authorization_url(
        self,
        client_creds,
        nonce,
        state=None,
        prompt=None,
        display=None,
        login_hint=None,
        access_type=None,
        include_granted_scopes=None,
        openid_realm=None,
        hd=None,
        response_type=None,
        scopes=None,
    ):
        """ 
        First step of OAuth2 authoriztion code flow. Creates an OAuth2 authorization URI.

        Arguments:

            client_creds (aiogoogle.auth.creds.ClientCreds):  A client_creds object/dictionary containing the following items:

                * client_id

                * scopes

                    * The scope value must begin with the string openid and then include profile or email or both.

                * redirect_uri

            nonce (str): A random value generated by your app that enables replay protection.

            scopes (list): List of OAuth2 scopes to ask for

                * Optional

                * Overrides the list of scopes specified in client creds

                * Some OpenID scopes that you can include: ['email', 'profile', 'openid']

            display (str):
            
                * An ASCII string value for specifying how the authorization server displays the authentication and consent user interface pages.
                
                * The following values are specified, and accepted by the Google servers, but do not have any effect on its behavior:
                
                    * ``page``
                    
                    * ``popup``
                    
                    * ``touch``
                    
                    * ``wap``

            state (str): A CSRF token

                * Optional

                * Specifies any string value that your application uses to maintain state between your authorization request and the authorization server's response.
                
                * The server returns the exact value that you send as a name=value pair in the hash (#) fragment of the redirect_uri after the user consents to or denies your application's access request.

                * You can use this parameter for several purposes, such as:
                
                    * Directing the user to the correct resource in your application
                    
                    * Sending nonces
                    
                    * Mitigating cross-site request forgery.

                * If no state is passed, this method will generate and add a secret token to ``user_creds['state']``.
                    
                * Since your redirect_uri can be guessed, using a state value can increase your assurance that an incoming connection is the result of an authentication request.
                
                * If you generate a random string or encode the hash of a cookie or another value that captures the client's state, you can validate the response to additionally ensure that the request and response originated in the same browser, providing protection against attacks such as cross-site request forgery.

            access_type (str): Indicates whether your application can refresh access tokens when the user is not present at the browser. Options:

                * Optional

                * ``"online"`` *Default*

                * ``"offline"`` Choose this for a refresheable/long-term access token

            include_granted_scopes (bool):
            
                * Optional

                * Enables applications to use incremental authorization to request access to additional scopes in context.
                
                * If you set this parameter's value to ``True`` and the authorization request is granted, then the new access token will also cover any scopes to which the user previously granted the application access.

            login_hint (str):
            
                * Optional
                
                * If your application knows which user is trying to authenticate, it can use this parameter to provide a hint to the Google Authentication Server.
                
                * The server uses the hint to simplify the login flow either by prefilling the email field in the sign-in form or by selecting the appropriate multi-login session.

                * Set the parameter value to an email address or sub identifier, which is equivalent to the user's Google ID.

                * This can help you avoid problems that occur if your app logs in the wrong user account.

            prompt (str):

                * Optional
                
                * A space-delimited, case-sensitive list of prompts to present the user.
                
                * If you don't specify this parameter, the user will be prompted only the first time your app requests access.
                
                * Possible values are:

                    * ``None`` : Default: Do not display any authentication or consent screens. Must not be specified with other values.

                    * ``'consent'`` : Prompt the user for consent.

                    * ``'select_account'`` : Prompt the user to select an account.

            openid_realm (str):

                * openid.realm is a parameter from the OpenID 2.0 protocol.
                
                * It is used in OpenID 2.0 requests to signify the URL-space for which an authentication request is valid.
                
                * Use openid.realm if you are migrating an existing application from OpenID 2.0 to OpenID Connect.
                
                * For more details, see Migrating off of OpenID 2.0. https://developers.google.com/identity/protocols/OpenID2Migration

            hd (str):

                * The hd (hosted domain) parameter streamlines the login process for G Suite hosted accounts.
                
                * By including the domain of the G Suite user (for example, mycollege.edu), you can indicate that the account selection UI should be optimized for accounts at that domain.
                
                * To optimize for G Suite accounts generally instead of just one domain, use an asterisk: hd=*.

                * Don't rely on this UI optimization to control who can access your app, as client-side requests can be modified.
                
                * Be sure to validate that the returned ID token has an hd claim value that matches what you expect (e.g. mycolledge.edu).
                
                * Unlike the request parameter, the ID token claim is contained within a security token from Google, so the value can be trusted.

            response_type (str):

                * OAuth2 response type

                * Defaults to Authorization Code Flow response type

        Note:

            It is highly recommended that you don't leave ``state`` as ``None`` in production

            To effortlessly create a random secret to pass it as a state token, you can use ``aiogoogle.auth.utils.create_secret()``

        Note:

            A Note About Scopes:

            * You can mix OAuth2 scopes with OpenID connect scopes. e.g.: ``openid email https://www.googleapis.com/auth/urlshortener``

            * For a list of all of Google's available scopes: https://developers.google.com/identity/protocols/googlescopes

            * It is recommended that your application requests access to authorization scopes in context whenever possible.
            
            * By requesting access to user data in context, via incremental authorization, you help users to more easily understand why your application needs the access it is requesting.

        Warning:

            * When listening for a callback after redirecting a user to the URL returned from this method, take the following into consideration:
            
                * If your response endpoint renders an HTML page, any resources on that page will be able to see the authorization code in the URL.
                
                * Scripts can read the URL directly, and the URL in the Referer HTTP header may be sent to any or all resources on the page.

                * Carefully consider whether you want to send authorization credentials to all resources on that page (especially third-party scripts such as social plugins and analytics).
                
                * To avoid this issue, it's recommend that the server first handle the request, then redirect to another URL that doesn't include the response parameters.

        Example:

            ::

                from aiogoogle.auth.utils import create_secret
                from aiogoogle import ClinetCreds

                client_creds = ClientCreds(
                    client_id='a_client_id',
                    scopes=['first.scope', 'second.scope'],
                    redirect_uri='http://localhost:8080'
                )

                state = create_secret()
                nonce = create_secret()

                auth_uri = openid_connect.authorization_url(
                    client_creds=client_creds,
                    nonce=nonce,
                    state=state,
                    access_type='offline',
                    include_granted_scopes=True,
                    login_hint='example@gmail.com',
                    prompt='select_account'
                    )

        Returns:

            (str): An Authorization URI
        """
        raise NotImplementedError

    @abstractmethod
    def build_user_creds(
        self, grant, client_creds, grant_type=None, nonce=None, hd=None, verify=True
    ):
        """
        Second step of Oauth2 authrization code flow and OpenID connect. Creates a User Creds object with access and refresh token

        Arguments:

            grant (str):
            
                * Aka: "code". 
                
                * The code received at your redirect URI from the auth callback

            client_creds (aiogoogle.auth.creds.ClientCreds):

                * Dict with client_id and client_secret items

            grant_type (str):

                * OAuth2 grant type

                * defaults to ``code`` (Authorization code flow)

            nonce (str):

                * Random value that prevents replay attacks

                * pass the one you used with ``self.authorization_url()`` method

            hd (str):

                * hosted domain for G-suite

                * used for id_token verification

            verify (str):

                * Whether or not to verify the received id_token

                * Unless you're building a speed critical application AND you're receiving your tokens directly from Google, you should leave this as True.

        Returns:

            aiogoogle.auth.creds.UserCreds: User Credentials with the following items:

                * ``access_token``

                * ``refresh_token``

                * ``expires_in`` (JSON format ISO 8601)

                * ``token_type`` always set to bearer

                * ``scopes``

        Raises:

            aiogoogle.excs.AuthError: Auth Error
        """
        raise NotImplementedError

    @abstractmethod
    def decode_and_validate(self, id_token_jwt, client_id=None, nonce=None, hd=None):
        """
        Decodes then validates an openid_connect jwt with Google's oaauth2 certificates

        Arguments:

            id_token_jwt (str): Found in :class:aiogoogle.auth.creds.UserCreds

            client_id (str): If provided will validate token's audience ('aud')

            nonce (str): If provided, will validate the nonce provided at authorization

            hd (str): If provided, will validate client's hosted domain

        Returns:

            dict: Decoded OpenID connect JWT
        """
        raise NotImplementedError

    @abstractmethod
    def get_user_info(self, user_creds):
        """
        https://developers.google.com/+/web/api/rest/openidconnect/getOpenIdConnect
    
        People: getOpenIdConnect
    
        Get user information after performing an OpenID connect flow.
    
        Use this method instead of people.get (Google+ API) when you need the OpenID Connect format.
    
        This method is not discoverable nor is it in the Google API client libraries. 
        
        To learn more, see OpenID Connect for sign-in. https://developers.google.com/+/web/api/rest/openidconnect/index.html
    
        Example:
    
            ::
    
                >>> await get_user_info(user_creds)
                {
                    "kind": "plus#personOpenIdConnect",
                    "gender": string,
                    "sub": string,
                    "name": string,
                    "given_name": string,
                    "family_name": string,
                    "profile": string,
                    "picture": string,
                    "email": string,
                    "email_verified": "true",
                    "locale": string,
                    "hd": string
                }

        Arguments:

            user_creds (aiogoogle.auth.creds.UserCreds): User credentials
        """
        raise NotImplementedError


class AbstractAPIKeyManager(ABC):
    @abstractmethod
    def authorize(self, request, api_key):
        """
        Adds API Key authorization query argument to URL of a request given an API key

        Arguments:

            request (aiogoogle.models.Request):

                Request to authorize

            creds (aiogoogle.auth.creds.ApiKey):

                ApiKey to refresh with

        Returns:

            aiogoogle.models.Request: Request with API key in URL
        """
        raise NotImplementedError
