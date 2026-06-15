import pytest

from app.utils.custom_response_codes import ResponseCode

# Tests for login

def test_login_success(test_client, create_test_user):
    create_test_user()

    response = test_client.post("/v1/auth/login", json={
        "username": "test_user",
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
        "username": "not_found_user",
        "password": "password123",
    })

    assert response.status_code == 401

    data = response.json()
    assert data["business_code"] == ResponseCode.INVALID_CREDENTIALS


def test_login_wrong_password(test_client, create_test_user):
    create_test_user()

    response = test_client.post("/v1/auth/login", json={
        "username": "test_user",
        "password": "password1234",
    })

    assert response.status_code == 401

    data = response.json()
    assert data["business_code"] == ResponseCode.INVALID_CREDENTIALS


@pytest.mark.parametrize("payload", [
    {},
    {"username": "test_user"},
    {"password": "123456"},
    {"username": 123, "password": "123"},
])
def test_login_invalid_input(test_client, payload):
    response = test_client.post("/v1/auth/login", json=payload)
    assert response.status_code == 422

# ------------------------------------------------------------------

# Tests for signup

def test_signup_success(test_client):
    response = test_client.post("/v1/auth/signup", json={
        "username": "John123!",
        "password": "password123",
        "email": "test2@example.com"
    })

    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert "access_token" in data["data"]
    assert "token_type" in data["data"]

    # assert "set-cookie" in response.headers
    assert "refresh_token" in response.cookies

    assert data["data"]["token_type"] == "Bearer"
    assert data["business_code"] == ResponseCode.SIGNUP_SUCCESSFUL


def test_signup_user_already_exists(test_client, create_test_user):
    create_test_user()

    response = test_client.post("/v1/auth/signup", json={
        "username": "John123!",
        "password": "password123",
        "email": "test@example.com"
    })

    assert response.status_code == 409

    data = response.json()
    assert data["business_code"] == ResponseCode.USER_ALREADY_EXISTS


@pytest.mark.parametrize("payload", [
    {},
    {"username": "test@example.com"},
    {"password": "123456"},
    {"username": 123, "email": "a", "password": "123"},
])
def test_signup_invalid_input(test_client, payload):
    response = test_client.post("/v1/auth/signup", json=payload)
    assert response.status_code == 422

# ------------------------------------------------------------------

# Tests for logout

def test_logout_success_auth_user(test_client, override_get_current_user):
    response = test_client.post("/v1/auth/logout")
    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert data["data"] is None
    assert data["business_code"] == ResponseCode.LOGOUT_SUCCESSFUL


def test_logout_not_auth_user(test_client):
    response = test_client.post("/v1/auth/logout")
    assert response.status_code == 401

# ------------------------------------------------------------------

# Tests for change password

def test_change_password_success_auth_user(test_client, override_get_current_user):
    response = test_client.post("/v1/auth/changepwd", json={
        "pwd": "Strongpassword123!",
        "new_pwd": "Newstrongpassword123!"
    })

    assert response.status_code == 200

    data = response.json()

    assert data["business_code"] == ResponseCode.SUCCESSFUL_PWD_CHANGE
    assert data["data"]["user_id"] == 1
    assert data["data"]["updated_at"] is not None



def test_change_password_wrong_old_password(test_client, override_get_current_user):
    response = test_client.post("/v1/auth/changepwd", json={
        "pwd": "Strongpassword1234!",
        "new_pwd": "Newstrongpassword123!"
    })

    assert response.status_code == 401

    data = response.json()
    assert data["business_code"] == ResponseCode.INVALID_OLD_PWD


def test_change_password_same_as_old(test_client, override_get_current_user):
    response = test_client.post("/v1/auth/changepwd", json={
        "pwd": "Strongpassword123!",
        "new_pwd": "Strongpassword123!"
    })

    assert response.status_code == 400

    data = response.json()
    assert data["business_code"] == ResponseCode.NEW_PASSWORD_SAME_AS_OLD


def test_change_password_not_auth_user(test_client):
    response = test_client.post("/v1/auth/changepwd", json={
        "pwd": "Strongpassword123!",
        "new_pwd": "Newstrongpassword123!"
    })

    assert response.status_code == 401

# ------------------------------------------------------------------