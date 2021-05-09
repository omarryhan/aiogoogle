#!/usr/bin/python3.7

import sys
import webbrowser
import asyncio
import pprint

from aiogoogle import Aiogoogle
from aiogoogle.auth.utils import create_secret
from aiogoogle.auth.managers import OOB_REDIRECT_URI

try:
    import yaml
except:  # noqa: E722  bare-except
    print('couldn\'t import yaml. Install "pyyaml" first')

sys.path.append("../..")

try:
    with open("keys.yaml", "r") as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
except Exception as e:
    print("Rename _keys.yaml to keys.yaml")
    raise e

EMAIL = config["user_creds"]["email"]
CLIENT_CREDS = {
    "client_id": config["client_creds"]["client_id"],
    "client_secret": config["client_creds"]["client_secret"],
    "scopes": config["client_creds"]["scopes"],
    "redirect_uri": OOB_REDIRECT_URI,
}


async def main():
    nonce = create_secret()
    aiogoogle = Aiogoogle(client_creds=CLIENT_CREDS)
    uri = aiogoogle.openid_connect.authorization_url(
        client_creds=CLIENT_CREDS,
        nonce=nonce,
        access_type="offline",
        include_granted_scopes=True,
        prompt="select_account",
    )
    webbrowser.open_new_tab(uri)
    grant = input("Paste the code you received here, then press Enter \n")
    full_user_creds = await aiogoogle.openid_connect.build_user_creds(
        grant=grant, client_creds=CLIENT_CREDS, nonce=nonce, verify=False
    )
    full_user_info = await aiogoogle.openid_connect.get_user_info(full_user_creds)
    print(
        f"full_user_creds: {pprint.pformat(full_user_creds)}\n\nfull_user_info: {pprint.pformat(full_user_info)}"
    )


if __name__ == "__main__":
    asyncio.run(main())
