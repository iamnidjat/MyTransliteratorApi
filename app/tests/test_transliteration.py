def test_transliterate_cyrillic_to_latin_az_success_auth_user(test_client, db, override_get_optional_current_user):
    response = test_client.post("/v1/transliteration/az/cyrillic-to-latin", json={"text": "Салам, бугун һава сон дərəcə гөзəлдир!"})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response
    assert data["data"]["result_text"] == "Salam, bugün hava son dərəcə gözəldir!"
    assert data["data"]["unrecognized_symbols"] == []

    assert len(db.execute("SELECT * FROM transliterations").fetchall()) == 1

def test_transliterate_cyrillic_to_latin_az_success_anonymous_user(test_client, db):
    response = test_client.post("/v1/transliteration/az/cyrillic-to-latin", json={"text": "Салам, бугун һава сон дərəcə гөзəлдир!"})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response
    assert data["data"]["result_text"] == "Salam, bugün hava son dərəcə gözəldir!"
    assert data["data"]["unrecognized_symbols"] == []

    assert len(db.execute("SELECT * FROM transliterations").fetchall()) == 0


def test_transliterate_cyrillic_to_latin_az_success_with_unknown_symbol_auth_user(test_client, db, override_get_optional_current_user):
    response = test_client.post("/v1/transliteration/az/cyrillic-to-latin", json={"text": "Салам#"})
    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    assert data["data"]["result_text"] == "Salam?"
    assert data["data"]["unrecognized_symbols"] == ["#"]

    assert len(db.execute("SELECT * FROM transliterations").fetchall()) == 1


def test_transliterate_cyrillic_to_latin_az_success_with_unknown_symbol_anonymous_user(test_client, db):
    response = test_client.post("/v1/transliteration/az/cyrillic-to-latin", json={"text": "Салам#"})
    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    assert data["data"]["result_text"] == "Salam?"
    assert data["data"]["unrecognized_symbols"] == ["#"]

    assert len(db.execute("SELECT * FROM transliterations").fetchall()) == 0


def test_transliterate_cyrillic_to_latin_az_with_empty_text(test_client, db):
    # no need for override_get_optional_current_user fixture, because empty input should not be saved to DB regardless of authentication status
    response = test_client.post("/v1/transliteration/az/cyrillic-to-latin", json={"text": ""})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response
    assert data["data"]["result_text"] == ""
    assert data["data"]["unrecognized_symbols"] == []

    assert len(db.execute("SELECT * FROM transliterations").fetchall()) == 0

def test_transliterate_cyrillic_to_latin_az_with_empty_input(test_client):
    response = test_client.post("/v1/transliteration/az/cyrillic-to-latin", json={})
    assert response.status_code == 422

def test_transliterate_cyrillic_to_latin_az_with_wrong_input_type(test_client):
    response = test_client.post("/v1/transliteration/az/cyrillic-to-latin", json={"text": 123})
    assert response.status_code == 422

def test_transliterate_cyrillic_to_latin_az_with_none_input(test_client):
    response = test_client.post("/v1/transliteration/az/cyrillic-to-latin", json={"text": None})
    assert response.status_code == 422

# -------------------------------------------------------------