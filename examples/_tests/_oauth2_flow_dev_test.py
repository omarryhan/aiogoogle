#!/usr/bin/python3.7

import sys, os, webbrowser, json

try:
    import yaml
except:
    print('couldn\'t import yaml. Install "pyyaml" first')

sys.path.append("../..")


from sanic import Sanic, response
from sanic.exceptions import ServerError

from aiogoogle import Aiogoogle, GoogleAPI, AuthError
from aiogoogle.auth.utils import create_secret

try:
    with open("../keys.yaml", "r") as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
except Exception as e:
    print("Rename _keys.yaml to keys.yaml")
    raise e

EMAIL = config["user_creds"]["email"]
CLIENT_CREDS = {
    "client_id": config["client_creds"]["client_id"],
    "client_secret": config["client_creds"]["client_secret"],
    "scopes": config["client_creds"]["scopes"],
    "redirect_uri": "http://localhost:5000/callback/aiogoogle",
}
state = create_secret()


LOCAL_ADDRESS = "localhost"
LOCAL_PORT = "5000"

app = Sanic(__name__)
aiogoogle = Aiogoogle(client_creds=CLIENT_CREDS)


async def refresh(full_user_creds):
    return await aiogoogle.oauth2.refresh(full_user_creds, CLIENT_CREDS)


def expire_creds_then_refresh(full_user_creds):
    import datetime

    full_user_creds["expires_at"] = (
        datetime.datetime.fromisoformat(full_user_creds["expires_at"])
        - datetime.timedelta(seconds=3480)
    ).isoformat()
    assert aiogoogle.oauth2.is_expired(full_user_creds) is True


async def revoke(full_user_creds):
    return await aiogoogle.oauth2.revoke(full_user_creds)


@app.route("/authorize")
def authorize(request):
    if aiogoogle.oauth2.is_ready(CLIENT_CREDS):
        uri = aiogoogle.oauth2.authorization_url(
            client_creds=CLIENT_CREDS,
            state=state,
            access_type="offline",
            include_granted_scopes=True,
            login_hint=EMAIL,
            prompt="select_account",
        )
        return response.redirect(uri)
    else:
        raise ServerError("Client doesn't have enough info for Oauth2")


@app.route("/callback/aiogoogle")
async def callback(request):
    if request.args.get("error"):
        return response.text("whoops!", 401)
    elif request.args.get("code"):
        returned_state = request.args["state"][0]
        if returned_state != state:
            raise ServerError("NO")
        full_user_creds = await aiogoogle.oauth2.build_user_creds(
            grant=request.args.get("code"), client_creds=CLIENT_CREDS
        )
        await refresh(full_user_creds)
        expire_creds_then_refresh(full_user_creds)
        await revoke(full_user_creds)
        return response.text("passed")


if __name__ == "__main__":
    webbrowser.open("http://" + LOCAL_ADDRESS + ":" + LOCAL_PORT + "/authorize")
    app.run(host=LOCAL_ADDRESS, port=LOCAL_PORT, debug=True)
