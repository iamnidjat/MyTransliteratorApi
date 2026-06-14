import pytest

from app.utils.custom_response_codes import ResponseCode

# Tests for login

def test_login_success(test_client, create_test_user):
    create_test_user()

    response = test_client.post("/v1/auth/login", json={
        "username": "test@example.com",
        "password": "password123",
    })

    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert "access_token" in data["data"]
    assert "token_type" in data["data"]

    # assert "set-cookie" in response.headers
    assert "refresh_token" in response.cookies

    assert data["data"]["token_type"] == "Bearer"
    assert data["business_code"] == ResponseCode.LOGIN_SUCCESSFUL


def test_login_user_not_found(test_client, create_test_user):
    # create_test_user() could be either used or not used

    response = test_client.post("/v1/auth/login", json={
        "username": "not_found_user@example.com",
        "password": "password123",
    })

    assert response.status_code == 401

    data = response.json()
    assert data["business_code"] == ResponseCode.INVALID_CREDENTIALS


def test_login_wrong_password(test_client, create_test_user):
    create_test_user()

    response = test_client.post("/v1/auth/login", json={
        "username": "test@example.com",
        "password": "password1234",
    })

    assert response.status_code == 401

    data = response.json()
    assert data["business_code"] == ResponseCode.INVALID_CREDENTIALS


@pytest.mark.parametrize("payload", [
    {},
    {"username": "test@example.com"},
    {"password": "123456"},
    {"username": 123, "password": "123"},
])
def test_login_invalid_input(test_client, payload):
    response = test_client.post("/v1/auth/login", json=payload)
    assert response.status_code == 422

# ------------------------------------------------------------------

# Tests for signup