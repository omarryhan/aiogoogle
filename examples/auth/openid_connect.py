#!/usr/bin/python3.7

import sys
import webbrowser
import pprint

from aiohttp.web import RouteTableDef, Application, run_app, Response, json_response, HTTPFound

from aiogoogle import Aiogoogle
from aiogoogle.auth.utils import create_secret

try:
    import yaml
except:  # noqa: E722  bare-except
    print('couldn\'t import yaml. Install "pyyaml" first')
    sys.exit(-1)

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
    "redirect_uri": "http://localhost:5000/callback/aiogoogle",
}
state = (
    create_secret()
)  # Shouldn't be a global or a hardcoded variable. should be tied to a session or a user and shouldn't be used more than once
nonce = (
    create_secret()
)  # Shouldn't be a global or a hardcoded variable. should be tied to a session or a user and shouldn't be used more than once


LOCAL_ADDRESS = "localhost"
LOCAL_PORT = 5000

routes = RouteTableDef()
aiogoogle = Aiogoogle(client_creds=CLIENT_CREDS)

# ----------------------------------------#
#                                        #
# **Step A (Check OAuth2 figure above)** #
#                                        #
# ----------------------------------------#


@routes.get("/authorize")
def authorize(request):
    if aiogoogle.openid_connect.is_ready(CLIENT_CREDS):
        uri = aiogoogle.openid_connect.authorization_url(
            client_creds=CLIENT_CREDS,
            state=state,
            nonce=nonce,
            access_type="offline",
            include_granted_scopes=True,
            login_hint=EMAIL,
            prompt="select_account",
        )
        # Step A
        raise HTTPFound(uri)
    else:
        return Response(text="Client doesn't have enough info for Oauth2", status=500)


# ----------------------------------------------#
#                                              #
# **Step B (Check OAuth2 figure above)**       #
#                                              #
# ----------------------------------------------#
# NOTE:                                        #
#  you should now be authorizing your app @    #
#   https://accounts.google.com/o/oauth2/      #
# ----------------------------------------------#

# ----------------------------------------------#
#                                              #
# **Step C, D & E (Check OAuth2 figure above)**#
#                                              #
# ----------------------------------------------#

# Step C
# Google should redirect current_user to
# this endpoint with a grant code
@routes.get("/callback/aiogoogle")
async def callback(request):
    if request.query.get("error"):
        error = {
            "error": request.query.get("error"),
            "error_description": request.query.get("error_description"),
        }
        return json_response(error)
    elif request.query.get("code"):
        returned_state = request.query["state"]
        # Check state
        if returned_state != state:
            return Response(text="NO", status=500)
        # Step D & E (D send grant code, E receive token info)
        full_user_creds = await aiogoogle.openid_connect.build_user_creds(
            grant=request.query.get("code"),
            client_creds=CLIENT_CREDS,
            nonce=nonce,
            verify=False,
        )
        full_user_info = await aiogoogle.openid_connect.get_user_info(full_user_creds)
        return Response(
            text=f"full_user_creds: {pprint.pformat(full_user_creds)}\n\nfull_user_info: {pprint.pformat(full_user_info)}"
        )
    else:
        # Should either receive a code or an error
        return Response(text="Something's probably wrong with your callback", status=400)


if __name__ == "__main__":
    app = Application()
    app.add_routes(routes)

    webbrowser.open("http://" + LOCAL_ADDRESS + ":" + str(LOCAL_PORT) + "/authorize")
    run_app(app, host=LOCAL_ADDRESS, port=LOCAL_PORT)
