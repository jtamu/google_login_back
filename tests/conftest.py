import pytest
import subprocess
import time
import os
from datetime import datetime
import requests
import boto3

ssm = boto3.client("ssm")

AUTH0_CLIENT_ID = ssm.get_parameter(Name="/auth0/client_id")["Parameter"]["Value"]
AUTH0_CLIENT_SECRET = ssm.get_parameter(Name="/auth0/client_secret")["Parameter"]["Value"]
AUTH0_TEST_USER_NAME = ssm.get_parameter(Name="/auth0/test-user01/name")["Parameter"]["Value"]
AUTH0_TEST_USER_PASSWORD = ssm.get_parameter(Name="/auth0/test-user01/password")["Parameter"]["Value"]

STAGE = os.getenv('STAGE')

DB_ENDPOINT = "http://dynamo-test:8000"
if STAGE == "ci":
    DB_ENDPOINT = "http://localhost:8003"


@pytest.fixture(scope="session", autouse=True)
def start_chalice_local():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"/var/log/{timestamp}.log"

    print(f"stage: {STAGE}")

    with open(filename, "w") as f:
        process = subprocess.Popen(
            ["chalice", "local", "--host=0.0.0.0", f"--port={os.getenv('TEST_PORT')}", f"--stage={STAGE}"],
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True,
        )

    # サービスが完全に起動するまで待機
    time.sleep(5)
    yield
    process.terminate()
    process.wait()

    with open(filename, "r") as f:
        print("\nchalice output:\n", f.read())


@pytest.fixture(scope="session")
def token():
    data = {
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": "my-custom-api",
        "username": AUTH0_TEST_USER_NAME,
        "password": AUTH0_TEST_USER_PASSWORD,
        "grant_type": "password",
    }

    res = requests.post("https://dev-yj8jxr3h2g1b3j0k.us.auth0.com/oauth/token", data)

    yield res.json()["access_token"]


@pytest.fixture(scope="session", autouse=True)
def create_table():
    sub_env = os.environ.copy()
    sub_env["DB_ENDPOINT"] = DB_ENDPOINT
    subprocess.run(args=["python", "create_table.py"], env=sub_env)
    yield
