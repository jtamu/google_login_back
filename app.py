from chalice import Chalice, Response, CORSConfig
import logging
import requests
import boto3
import urllib
import jwt
from chalicelib.models import Users, Microposts
from chalicelib.utils import login


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


@app.route("/microposts", methods=["POST"], cors=CORSConfig(allow_origin="https://google-login.jtamu-sample-app.link"))
def post():
    req = app.current_request.json_body or {}
    if "content" not in req:
        return Response(body={"message": "server error"}, status_code=500)

    try:
        user = login(app, CLIENT_ID)
    except Exception:
        return Response(body={"message": "server error"}, status_code=500)

    micropost = user.post(req["content"])
    micropost.save()

    return Response(body={"posted_at": micropost.postedAt.isoformat()}, status_code=201)


@app.route("/microposts", methods=["GET"], cors=CORSConfig(allow_origin="https://google-login.jtamu-sample-app.link"))
def get_list():
    try:
        user = login(app, CLIENT_ID)
    except Exception:
        return Response(body={"message": "server error"}, status_code=500)

    posts = Microposts.query(user.id)
    res = [post.to_simple_dict() for post in posts]
    return Response(body=res, status_code=200)
