#!/usr/bin/python3.7

import sys

try:
    import yaml
except:  # noqa: E722  bare-except
    print('couldn\'t import yaml. Install "pyyaml" first')

sys.path.append("..")

from aiogoogle import Aiogoogle  # noqa: F401  imported but unused
from aiogoogle.auth.creds import UserCreds, ClientCreds, ApiKey  # noqa: F401  imported but unused

try:
    with open("keys.yaml", "r") as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
except Exception as e:
    print("Rename _keys.yaml to keys.yaml")
    raise e

email = config["user_creds"]["email"]

user_creds = UserCreds(
    access_token=config["user_creds"]["access_token"],
    refresh_token=config["user_creds"]["refresh_token"],
    expires_at=config["user_creds"]["expires_at"],
)

api_key = ApiKey(config["api_key"])

client_creds = ClientCreds(
    client_id=config["client_creds"]["client_id"],
    client_secret=config["client_creds"]["client_secret"],
    scopes=config["client_creds"]["scopes"],
)
