def provider_state(name, **params):
    pass


def test_pacts(pact_verifier):
    pact_verifier.verify("http://localhost:8002", provider_state)
