OAUTH2_V2_DISCVOCERY_DOC = {
    "auth": {
        "oauth2": {
            "scopes": {
                "https://www.googleapis.com/auth/plus.login": {
                    "description": "Know the list of people in your circles, your age range, and "
                    "language"
                },
                "https://www.googleapis.com/auth/plus.me": {
                    "description": "Know who you are on Google"
                },
                "https://www.googleapis.com/auth/userinfo.email": {
                    "description": "View your email address"
                },
                "https://www.googleapis.com/auth/userinfo.profile": {
                    "description": "View your basic profile info"
                },
            }
        }
    },
    "basePath": "/",
    "baseUrl": "https://www.googleapis.com/",
    "batchPath": "batch/oauth2/v2",
    "description": "Obtains end-user authorization grants for use with other Google APIs.",
    "discoveryVersion": "v1",
    "documentationLink": "https://developers.google.com/accounts/docs/OAuth2",
    "etag": '"J3WqvAcMk4eQjJXvfSI4Yr8VouA/fwW2utFkCnVanfAd4kn3jkF7-Z8"',
    "icons": {
        "x16": "https://www.gstatic.com/images/branding/product/1x/googleg_16dp.png",
        "x32": "https://www.gstatic.com/images/branding/product/1x/googleg_32dp.png",
    },
    "id": "oauth2:v2",
    "kind": "discovery#restDescription",
    "methods": {
        "getCertForOpenIdConnect": {
            "httpMethod": "GET",
            "id": "oauth2.getCertForOpenIdConnect",
            "path": "oauth2/v2/certs",
            "response": {"$ref": "Jwk"},
        },
        "tokeninfo": {
            "httpMethod": "POST",
            "id": "oauth2.tokeninfo",
            "parameters": {
                "access_token": {"location": "query", "type": "string"},
                "id_token": {"location": "query", "type": "string"},
                "token_handle": {"location": "query", "type": "string"},
            },
            "path": "oauth2/v2/tokeninfo",
            "response": {"$ref": "Tokeninfo"},
        },
    },
    "name": "oauth2",
    "ownerDomain": "google.com",
    "ownerName": "Google",
    "parameters": {
        "alt": {
            "default": "json",
            "description": "Data format for the response.",
            "enum": ["json"],
            "enumDescriptions": ["Responses with Content-Type of application/json"],
            "location": "query",
            "type": "string",
        },
        "fields": {
            "description": "Selector specifying which fields to include in a partial response.",
            "location": "query",
            "type": "string",
        },
        "key": {
            "description": "API key. Your API key identifies your project and provides you with API access, quota, and reports. Required unless "
            "you provide an OAuth 2.0 token.",
            "location": "query",
            "type": "string",
        },
        "oauth_token": {
            "description": "OAuth 2.0 token for the current user.",
            "location": "query",
            "type": "string",
        },
        "prettyPrint": {
            "default": "true",
            "description": "Returns response with indentations and line breaks.",
            "location": "query",
            "type": "boolean",
        },
        "quotaUser": {
            "description": "An opaque string that represents a user for quota purposes. Must not exceed 40 characters.",
            "location": "query",
            "type": "string",
        },
        "userIp": {
            "description": "Deprecated. Please use quotaUser instead.",
            "location": "query",
            "type": "string",
        },
    },
    "protocol": "rest",
    "resources": {
        "userinfo": {
            "methods": {
                "get": {
                    "httpMethod": "GET",
                    "id": "oauth2.userinfo.get",
                    "path": "oauth2/v2/userinfo",
                    "response": {"$ref": "Userinfoplus"},
                    "scopes": [
                        "https://www.googleapis.com/auth/plus.login",
                        "https://www.googleapis.com/auth/plus.me",
                        "https://www.googleapis.com/auth/userinfo.email",
                        "https://www.googleapis.com/auth/userinfo.profile",
                    ],
                }
            },
            "resources": {
                "v2": {
                    "resources": {
                        "me": {
                            "methods": {
                                "get": {
                                    "httpMethod": "GET",
                                    "id": "oauth2.userinfo.v2.me.get",
                                    "path": "userinfo/v2/me",
                                    "response": {"$ref": "Userinfoplus"},
                                    "scopes": [
                                        "https://www.googleapis.com/auth/plus.login",
                                        "https://www.googleapis.com/auth/plus.me",
                                        "https://www.googleapis.com/auth/userinfo.email",
                                        "https://www.googleapis.com/auth/userinfo.profile",
                                    ],
                                }
                            }
                        }
                    }
                }
            },
        }
    },
    "revision": "20181105",
    "rootUrl": "https://www.googleapis.com/",
    "schemas": {
        "Jwk": {
            "id": "Jwk",
            "properties": {
                "keys": {
                    "items": {
                        "properties": {
                            "alg": {"default": "RS256", "type": "string"},
                            "e": {"type": "string"},
                            "kid": {"type": "string"},
                            "kty": {"default": "RSA", "type": "string"},
                            "n": {"type": "string"},
                            "use": {"default": "sig", "type": "string"},
                        },
                        "type": "object",
                    },
                    "type": "array",
                }
            },
            "type": "object",
        },
        "Tokeninfo": {
            "id": "Tokeninfo",
            "properties": {
                "access_type": {
                    "description": "The access type granted with this token. It can be offline or online.",
                    "type": "string",
                },
                "audience": {
                    "description": "Who is the intended audience for this token. In general the same as issued_to.",
                    "type": "string",
                },
                "email": {
                    "description": "The email address of the user. Present only if the email scope is present in the request.",
                    "type": "string",
                },
                "expires_in": {
                    "description": "The expiry time of the token, as number of seconds left until expiry.",
                    "format": "int32",
                    "type": "integer",
                },
                "issued_to": {
                    "description": "To whom was the token issued to. In general the same as audience.",
                    "type": "string",
                },
                "scope": {
                    "description": "The space separated list of scopes granted to this token.",
                    "type": "string",
                },
                "token_handle": {
                    "description": "The token handle associated with this token.",
                    "type": "string",
                },
                "user_id": {"description": "The obfuscated user id.", "type": "string"},
                "verified_email": {
                    "description": "Boolean flag which is true if the email address is verified. Present only if the "
                    "email scope is present in the request.",
                    "type": "boolean",
                },
            },
            "type": "object",
        },
        "Userinfoplus": {
            "id": "Userinfoplus",
            "properties": {
                "email": {"description": "The user's email address.", "type": "string"},
                "family_name": {
                    "description": "The user's last name.",
                    "type": "string",
                },
                "gender": {"description": "The user's gender.", "type": "string"},
                "given_name": {
                    "description": "The user's first name.",
                    "type": "string",
                },
                "hd": {
                    "description": "The hosted domain e.g. example.com if the user is Google apps user.",
                    "type": "string",
                },
                "id": {
                    "description": "The obfuscated ID of the user.",
                    "type": "string",
                },
                "link": {"description": "URL of the profile page.", "type": "string"},
                "locale": {
                    "description": "The user's preferred locale.",
                    "type": "string",
                },
                "name": {"description": "The user's full name.", "type": "string"},
                "picture": {
                    "description": "URL of the user's picture image.",
                    "type": "string",
                },
                "verified_email": {
                    "default": "true",
                    "description": "Boolean flag which is true if the email address is verified. Always verified "
                    "because we only return the user's primary email address.",
                    "type": "boolean",
                },
            },
            "type": "object",
        },
    },
    "servicePath": "",
    "title": "Google OAuth2 API",
    "version": "v2",
}

WELLKNOWN_OPENID_CONFIGS = {
    "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
    "claims_supported": [
        "aud",
        "email",
        "email_verified",
        "exp",
        "family_name",
        "given_name",
        "iat",
        "iss",
        "name",
        "picture",
        "sub",
    ],
    "code_challenge_methods_supported": ["plain", "S256"],
    "device_authorization_endpoint": "https://oauth2.googleapis.com/device/code",
    "grant_types_supported": [
        "authorization_code",
        "refresh_token",
        "urn:ietf:params:oauth:grant-type:device_code",
        "urn:ietf:params:oauth:grant-type:jwt-bearer",
    ],
    "id_token_signing_alg_values_supported": ["RS256"],
    "issuer": "https://accounts.google.com",
    "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
    "response_types_supported": [
        "code",
        "token",
        "id_token",
        "code token",
        "code id_token",
        "token id_token",
        "code token id_token",
        "none",
    ],
    "revocation_endpoint": "https://oauth2.googleapis.com/revoke",
    "scopes_supported": ["openid", "email", "profile"],
    "subject_types_supported": ["public"],
    "token_endpoint": "https://oauth2.googleapis.com/token",
    "token_endpoint_auth_methods_supported": [
        "client_secret_post",
        "client_secret_basic",
    ],
    "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
}
