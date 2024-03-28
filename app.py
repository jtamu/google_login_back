from chalice import Chalice, Response, CORSConfig
import logging
import requests
import boto3
import urllib
import jwt
from chalicelib.models import Users


app = Chalice(app_name="google_login_back")
app.log.setLevel(logging.DEBUG)

ssm = boto3.client("ssm")

CLIENT_ID = ssm.get_parameter(Name="/google_oauth/client_id")["Parameter"]["Value"]
CLIENT_SECRET = ssm.get_parameter(Name="/google_oauth/client_secret")["Parameter"]["Value"]
REDIRECT_URI = ssm.get_parameter(Name="/google_oauth/redirect_uri")["Parameter"]["Value"]


@app.route("/get_token", methods=["POST"], cors=CORSConfig(allow_origin="https://google-login.jtamu-sample-app.link"))
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
    encoded = urllib.parse.urlencode(body)
    res = requests.post(
        "https://oauth2.googleapis.com/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=encoded,
    )
    if res.status_code >= 300:
        app.log.error(res.json())
        return Response(body={"message": "server error"}, status_code=500)

    return res.json()


@app.route("/login", methods=["POST"], cors=CORSConfig(allow_origin="https://google-login.jtamu-sample-app.link"))
def login():
    if "Authorization" not in app.current_request.headers:
        return Response(body={"message": "server error"}, status_code=500)

    id_token = app.current_request.headers["Authorization"].removeprefix("Bearer ")

    jwks_client = jwt.PyJWKClient("https://www.googleapis.com/oauth2/v3/certs")
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        payload = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
        )
    except Exception as e:
        app.log.error(e)
        return Response(body={"message": "server error"}, status_code=500)

    count = Users.count(payload["iss"], Users.subject == payload["sub"])
    if count == 0:
        u = Users(issuer=payload["iss"], subject=payload["sub"])
        u.save()

    return Response(body=None, status_code=201)
