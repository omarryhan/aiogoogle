# Examples

## Authentication instructions

### OAuth2

- Add http://localhost:5000/callback/aiogoogle as an allowed redirect URL
- Copy `_keys.yaml` and make a new file and name it `keys.yaml` that way its gitignored and readable by the examples here.

```sh
cd examples && cp _keys.yaml keys.yaml
```

- Atleast fill out the `client_id`, `client_secret` and `scopes` fields.
- Perform OAuth2 for personal use:

Run:

```sh
python auth/oauth2.py
```

To get OpenID Connect tokens as well, run this intead:

```sh
python auth/openid_connect.py
```

If you'll only be using the examples here on your desktop, you can use the CLI authentication script. With this script you won't have to specify a redirect URL nor a value javascript origin, but you have to choose "Desktop Application" when creating your credentials:

```sh
python auth/openid_connect_cli.py
```

- Now copy and paste the access token and refresh token you just generated and paste them in your keys.yaml file. You're now ready to run the examples in this folder.


### Service account auth

- Donwload a service account JSON key file, put it in this directory and name it as `test_service_account.json`. It will be gitignored.
