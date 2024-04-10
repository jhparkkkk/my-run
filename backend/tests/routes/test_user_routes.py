from fastapi.testclient import TestClient
from app.api.main import app

import responses

@responses.activate
def test_signup_redirect():
    client = TestClient(app)

    response = client.get("/signup", follow_redirects=True)


    final_url = response.url 
    expected_url_start = "http://www.strava.com/oauth/authorize"
    assert str(final_url).startswith(expected_url_start)
    assert response.status_code == 200
