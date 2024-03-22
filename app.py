from chalice import Chalice, Response
import logging
import requests
import boto3


app = Chalice(app_name="google_login_back")
app.log.setLevel(logging.DEBUG)

ssm = boto3.client("ssm")

CLIENT_ID = ssm.get_parameter(Name="/google_oauth/client_id")["Parameter"]["Value"]
CLIENT_SECRET = ssm.get_parameter(Name="/google_oauth/client_secret")["Parameter"]["Value"]
REDIRECT_URI = ssm.get_parameter(Name="/google_oauth/redirect_uri")["Parameter"]["Value"]


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
