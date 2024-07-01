import os


def provider_state(name, **params):
    pass


def test_pacts(pact_verifier, start_chalice_local):
    pact_verifier.verify(f"http://localhost:{os.getenv('TEST_PORT')}", provider_state)
