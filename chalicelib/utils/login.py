import jwt
from chalice import Chalice
from chalicelib.models import Users


def login(app: Chalice, client_id: str) -> Users:
    if "Authorization" not in app.current_request.headers:
        raise Exception

    id_token = app.current_request.headers["Authorization"].removeprefix("Bearer ")

    jwks_client = jwt.PyJWKClient("https://www.googleapis.com/oauth2/v3/certs")
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        payload = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client_id,
        )
    except Exception as e:
        app.log.error(e)
        raise Exception

    count = Users.count(payload["iss"], Users.subject == payload["sub"])
    if count == 0:
        u = Users(issuer=payload["iss"], subject=payload["sub"])
        u.save()

    return Users.get(payload["iss"], payload["sub"])
