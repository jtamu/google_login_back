import os
from chalice import Chalice, Response
import logging
import requests


app = Chalice(app_name="google_login_back")
app.log.setLevel(logging.DEBUG)

CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")


@app.route("/get_token", methods=["POST"])
def index():
    req = app.current_request.json_body or {}
    if "code" not in req:
        return Response(body={"message": "server error"}, status_code=500)

    body = {
        "code": req["code"],
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    res = requests.post("https://oauth2.googleapis.com/token", json=body)
    app.log.info(res.json())

    return {"hello": "world"}
