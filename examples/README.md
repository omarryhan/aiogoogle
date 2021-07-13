# Examples

## Authentication instructions

### OAuth2

#### Create your keys

Add http://localhost:5000/callback/aiogoogle as an allowed redirect URL

#### Create a key local key storage file

Copy `_keys.yaml` and make a new file and name it `keys.yaml` that way its gitignored and readable by the examples here.

```sh
cd examples && cp _keys.yaml keys.yaml
```

Atleast fill out the `client_id`, `client_secret` and `scopes` fields.

#### Run one of the authentication examples in the OAuth2 directory

For user OAuth2:

Run:

```sh
python auth/oauth2.py
```

For OpenID Connect, run:

```sh
python auth/openid_connect.py
```

For desktop applications, run:

```sh
python auth/openid_connect_cli.py
```

With this script you won't don't to specify a redirect URL nor a valid javascript origin. You just have to tell Google that it's a desktop app.

#### Copy the keys to `keys.yaml`

When you're done, copy and paste the access token and refresh token returned to you and paste them in your keys.yaml file.

You're now ready to run the examples in this folder.

### Service account auth

Donwload a service account JSON key file, put it in this directory and name it as `test_service_account.json`.

It will be gitignored.
