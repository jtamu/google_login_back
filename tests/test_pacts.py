import os
import requests


CHALICE_URL = f"http://localhost:{os.getenv('TEST_PORT')}"


def provider_state(token):
    def _provider_state(name, **params):
        if name == "ユーザの投稿が存在する場合":
            requests.post(f"{CHALICE_URL}/auth0/microposts", json={"content": "hello, world"}, headers={'Authorization': f"Bearer {token}"})
    return _provider_state


def test_pacts(pact_verifier, token):
    pact_verifier.verify(CHALICE_URL, provider_state(token), extra_provider_headers={'Authorization': f"Bearer {token}"})
