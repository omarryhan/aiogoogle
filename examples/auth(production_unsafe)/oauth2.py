#!/usr/bin/python3.7

import sys, os, webbrowser, json
try:
    import yaml
except:
    print('couldn\'t import yaml. Install "pyyaml" first')

sys.path.append("../..")

from sanic import Sanic, response
from sanic.exceptions import ServerError

from aiogoogle import Aiogoogle
from aiogoogle.auth.utils import create_secret

try:
    with open("../keys.yaml", "r") as stream:
        config = yaml.load(stream)
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
state = create_secret()  # Shouldn't be a global hardcoded variable.


LOCAL_ADDRESS = "localhost"
LOCAL_PORT = "5000"

app = Sanic(__name__)
aiogoogle = Aiogoogle(client_creds=CLIENT_CREDS)

# ----------------------------------------#
#                                        #
# **Step A (Check OAuth2 figure above)** #
#                                        #
# ----------------------------------------#


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
        # Step A
        return response.redirect(uri)
    else:
        raise ServerError("Client doesn't have enough info for Oauth2")


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
@app.route("/callback/aiogoogle")
async def callback(request):
    if request.args.get("error"):
        error = {
            "error": request.args.get("error"),
            "error_description": request.args.get("error_description"),
        }
        return response.json(error)
    elif request.args.get("code"):
        returned_state = request.args["state"][0]
        # Check state
        if returned_state != state:
            raise ServerError("NO")
        # Step D & E (D send grant code, E receive token info)
        full_user_creds = await aiogoogle.oauth2.build_user_creds(
            grant=request.args.get("code"), client_creds=CLIENT_CREDS
        )
        return response.json(full_user_creds)
    else:
        # Should either receive a code or an error
        return response.text("Something's probably wrong with your callback")


if __name__ == "__main__":
    webbrowser.open("http://" + LOCAL_ADDRESS + ":" + LOCAL_PORT + "/authorize")
    app.run(host=LOCAL_ADDRESS, port=LOCAL_PORT, debug=True)
