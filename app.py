from chalice import Chalice, Response, CORSConfig
import logging
import requests
import boto3
import urllib
from datetime import datetime, timedelta, timezone
from chalicelib.models import Microposts
from chalicelib.utils import login
import jwt


app = Chalice(app_name="google_login_back")
app.log.setLevel(logging.DEBUG)

ssm = boto3.client("ssm")

CLIENT_ID = ssm.get_parameter(Name="/google_oauth/client_id")["Parameter"]["Value"]
CLIENT_SECRET = ssm.get_parameter(Name="/google_oauth/client_secret")["Parameter"]["Value"]
REDIRECT_URI = ssm.get_parameter(Name="/google_oauth/redirect_uri")["Parameter"]["Value"]
AUTH0_CLIENT_ID = ssm.get_parameter(Name="/auth0/client_id")["Parameter"]["Value"]


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
    try:
        user = login(app, CLIENT_ID)
    except Exception:
        return Response(body={"message": "server error"}, status_code=500)

    req = app.current_request.json_body or {}
    if "content" not in req:
        return Response(body={"message": "server error"}, status_code=500)

    micropost = user.post(req["content"])
    micropost.save()

    if "access_token" in req:
        start, end, summary = _parse_schedule(req["content"])
        if start and end and summary:
            app.log.info(f"googleカレンダーに予定({summary})を作成します")
            token = req["access_token"]
            res = requests.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "summary": summary,
                    "description": "これはサンプルアプリで作成した予定です",
                    "start": {"dateTime": start.isoformat()},
                    "end": {"dateTime": end.isoformat()},
                },
            )
            if res.status_code >= 300:
                app.log.error(res.json())
                return Response(body={"message": "server error"}, status_code=500)

            app.log.info(f"googleカレンダーに予定({summary})を作成しました")

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


def _parse_schedule(schedule_str):
    # 文字列をスペースで分割して情報を取得
    parts = schedule_str.split()

    if len(parts) < 5 or parts[2] != "~":
        return None, None, None

    # 日付と時間をパースしてdatetimeオブジェクトに変換
    start_str = f"{parts[0]} {parts[1]}"
    end_str = f"{parts[3]} {parts[4]}"

    start = datetime.strptime(start_str, "%Y/%m/%d %H:%M").replace(tzinfo=timezone(timedelta(hours=9)))
    end = datetime.strptime(end_str, "%Y/%m/%d %H:%M").replace(tzinfo=timezone(timedelta(hours=9)))

    # サマリを取得
    summary = " ".join(parts[5:])

    return start, end, summary


@app.route("/auth0/microposts", methods=["GET"])
def get_micropost_for_auth0():
    if "Authorization" not in app.current_request.headers:
        return Response(body=None, status_code=401)

    access_token = app.current_request.headers["Authorization"].removeprefix("Bearer ")

    jwks_client = jwt.PyJWKClient("https://dev-yj8jxr3h2g1b3j0k.us.auth0.com/.well-known/jwks.json")
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        payload = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AUTH0_CLIENT_ID,
        )
    except Exception as e:
        app.log.error(e)
        return Response(body=None, status_code=401)

    posts = Microposts.query(payload.get("sub"))
    res = [post.to_simple_dict() for post in posts]
    return Response(body=res, status_code=200)
