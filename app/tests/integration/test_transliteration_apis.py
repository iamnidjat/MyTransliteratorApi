import pytest

# Tests for normal input

@pytest.mark.parametrize(
        "url, input_text, expected_result_text", 
        [
            ("/v1/transliteration/az/cyrillic-to-latin", "Салам, бугун һава сон дərəcə гөзəлдир", "Salam, bugün hava son dərəcə gözəldir"),
            ("/v1/transliteration/az/latin-to-cyrillic", "Salam, bugün hava son dərəcə gözəldir", "Салам, бугун һава сон дərəcə гөзəлдир")
        ]
    )
def test_transliteration_success_auth_user(test_client, db, override_get_optional_current_user, url, input_text, expected_result_text):
    response = test_client.post(url, json={"text": input_text})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response
    assert data["data"]["result_text"] == expected_result_text
    assert data["data"]["unrecognized_symbols"] == []

    rows = db.execute("SELECT * FROM transliterations").fetchall()
    assert len(rows) == 1


@pytest.mark.parametrize(
        "url, input_text, expected_result_text", 
        [
            ("/v1/transliteration/az/cyrillic-to-latin", "Салам, бугун һава сон дərəcə гөзəлдир", "Salam, bugün hava son dərəcə gözəldir"),
            ("/v1/transliteration/az/latin-to-cyrillic", "Salam, bugün hava son dərəcə gözəldir", "Салам, бугун һава сон дərəcə гөзəлдир")
        ]
    )
def test_transliteration_success_anonymous_user(test_client, db, url, input_text, expected_result_text):
    response = test_client.post(url, json={"text": input_text})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response 
    assert data["data"]["result_text"] == expected_result_text
    assert data["data"]["unrecognized_symbols"] == []

    rows = db.execute("SELECT * FROM transliterations").fetchall()
    assert len(rows) == 0


@pytest.mark.parametrize(
        "url, input_text, expected_result_text, unrecognized_symbols", 
        [
            ("/v1/transliteration/az/cyrillic-to-latin", "Салам#", "Salam?", ["#"]),
            ("/v1/transliteration/az/latin-to-cyrillic", "Salam#", "Салам?", ["#"])
        ]
    )
def test_transliteration_success_with_unknown_symbol_auth_user(test_client, db, override_get_optional_current_user, url, input_text, expected_result_text, unrecognized_symbols):
    response = test_client.post(url, json={"text": input_text})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response 
    assert data["data"]["result_text"] == expected_result_text
    assert data["data"]["unrecognized_symbols"] == unrecognized_symbols

    rows = db.execute("SELECT * FROM transliterations").fetchall()
    assert len(rows) == 1


@pytest.mark.parametrize(
        "url, input_text, expected_result_text, unrecognized_symbols", 
        [
            ("/v1/transliteration/az/cyrillic-to-latin", "Салам#", "Salam?", ["#"]),
            ("/v1/transliteration/az/latin-to-cyrillic", "Salam#", "Салам?", ["#"])
        ]
    )
def test_transliteration_success_with_unknown_symbol_anonymous_user(test_client, db, url, input_text, expected_result_text, unrecognized_symbols):
    response = test_client.post(url, json={"text": input_text})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response 
    assert data["data"]["result_text"] == expected_result_text
    assert data["data"]["unrecognized_symbols"] == unrecognized_symbols

    rows = db.execute("SELECT * FROM transliterations").fetchall()
    assert len(rows) == 0


@pytest.mark.parametrize(
        "url, input_text, expected_result_text", 
        [
            ("/v1/transliteration/az/cyrillic-to-latin", "", ""),
            ("/v1/transliteration/az/latin-to-cyrillic", "", "")
        ]
    )
def test_transliteration_with_empty_text(test_client, db, url, input_text, expected_result_text):
    # no need for override_get_optional_current_user fixture, because empty input should not be saved to DB regardless of authentication status
    response = test_client.post(url, json={"text": input_text})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response
    assert data["data"]["result_text"] == expected_result_text
    assert data["data"]["unrecognized_symbols"] == []

    rows = db.execute("SELECT * FROM transliterations").fetchall()
    assert len(rows) == 0


@pytest.mark.parametrize(
        "url, payload", 
        [
            # empty input
            ("/v1/transliteration/az/cyrillic-to-latin", {}),
            ("/v1/transliteration/az/latin-to-cyrillic", {}),

             # wrong input type
            ("/v1/transliteration/az/cyrillic-to-latin", {"text": 123}),
            ("/v1/transliteration/az/latin-to-cyrillic", {"text": 123}),

             # none input
            ("/v1/transliteration/az/cyrillic-to-latin", {"text": None}),
            ("/v1/transliteration/az/latin-to-cyrillic", {"text": None}),
        ]
    )
def test_transliteration_with_invalid_input(test_client, url, payload):
    response = test_client.post(url, json=payload)
    assert response.status_code == 422

# -------------------------------------------------------------

# Tests for file upload 

@pytest.mark.parametrize(
        "url, input_text, expected_result_text", 
        [
            ("/v1/transliteration/az/cyrillic-to-latin/file", "Салам, бугун һава сон дərəcə гөзəлдир", "Salam, bugün hava son dərəcə gözəldir"),
            ("/v1/transliteration/az/latin-to-cyrillic/file", "Salam, bugün hava son dərəcə gözəldir", "Салам, бугун һава сон дərəcə гөзəлдир")
        ]
    )
def test_transliteration_file_success_auth_user(test_client, db, override_get_optional_current_user, url, input_text, expected_result_text):
    file_content = input_text.encode("utf-8")
    response = test_client.post(url, files = {"file": ("test.txt", file_content, "text/plain")})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response
    assert data["data"]["result_text"] == expected_result_text
    assert data["data"]["unrecognized_symbols"] == []

    rows = db.execute("SELECT * FROM transliterations").fetchall()
    assert len(rows) == 1


@pytest.mark.parametrize(
        "url, input_text, expected_result_text", 
        [
            ("/v1/transliteration/az/cyrillic-to-latin/file", "Салам, бугун һава сон дərəcə гөзəлдир", "Salam, bugün hava son dərəcə gözəldir"),
            ("/v1/transliteration/az/latin-to-cyrillic/file", "Salam, bugün hava son dərəcə gözəldir", "Салам, бугун һава сон дərəcə гөзəлдир")
        ]
    )
def test_transliteration_file_success_anonymous_user(test_client, db, url, input_text, expected_result_text):
    file_content = input_text.encode("utf-8")
    response = test_client.post(url, files = {"file": ("test.txt", file_content, "text/plain")})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response 
    assert data["data"]["result_text"] == expected_result_text
    assert data["data"]["unrecognized_symbols"] == []

    rows = db.execute("SELECT * FROM transliterations").fetchall()
    assert len(rows) == 0


@pytest.mark.parametrize(
        "url, input_text, expected_result_text, unrecognized_symbols", 
        [
            ("/v1/transliteration/az/cyrillic-to-latin/file", "Салам#", "Salam?", ["#"]),
            ("/v1/transliteration/az/latin-to-cyrillic/file", "Salam#", "Салам?", ["#"])
        ]
    )
def test_transliteration_file_success_with_unknown_symbol_auth_user(test_client, db, override_get_optional_current_user, url, input_text, expected_result_text, unrecognized_symbols):
    file_content = input_text.encode("utf-8")
    response = test_client.post(url, files = {"file": ("test.txt", file_content, "text/plain")})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response 
    assert data["data"]["result_text"] == expected_result_text
    assert data["data"]["unrecognized_symbols"] == unrecognized_symbols

    rows = db.execute("SELECT * FROM transliterations").fetchall()
    assert len(rows) == 1


@pytest.mark.parametrize(
        "url, input_text, expected_result_text, unrecognized_symbols", 
        [
            ("/v1/transliteration/az/cyrillic-to-latin/file", "Салам#", "Salam?", ["#"]),
            ("/v1/transliteration/az/latin-to-cyrillic/file", "Salam#", "Салам?", ["#"])
        ]
    )
def test_transliteration_file_success_with_unknown_symbol_anonymous_user(test_client, db, url, input_text, expected_result_text, unrecognized_symbols):
    file_content = input_text.encode("utf-8")
    response = test_client.post(url, files = {"file": ("test.txt", file_content, "text/plain")})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response 
    assert data["data"]["result_text"] == expected_result_text
    assert data["data"]["unrecognized_symbols"] == unrecognized_symbols

    rows = db.execute("SELECT * FROM transliterations").fetchall()
    assert len(rows) == 0


@pytest.mark.parametrize(
        "url, input_text, expected_result_text", 
        [
            ("/v1/transliteration/az/cyrillic-to-latin/file", "", ""),
            ("/v1/transliteration/az/latin-to-cyrillic/file", "", "")
        ]
    )
def test_transliteration_file_with_empty_text(test_client, db, url, input_text, expected_result_text):
    # no need for override_get_optional_current_user fixture, because empty input should not be saved to DB regardless of authentication status
    file_content = input_text.encode("utf-8")
    response = test_client.post(url, files = {"file": ("test.txt", file_content, "text/plain")})
    assert response.status_code == 200

    data = response.json()

    # checking the structure of the response
    assert "data" in data
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]

    # checking the content of the response
    assert data["data"]["result_text"] == expected_result_text
    assert data["data"]["unrecognized_symbols"] == []

    rows = db.execute("SELECT * FROM transliterations").fetchall()
    assert len(rows) == 0


@pytest.mark.parametrize(
        "url", 
        [
            ("/v1/transliteration/az/cyrillic-to-latin/file"),
            ("/v1/transliteration/az/latin-to-cyrillic/file")
        ]
    )
def test_transliteration_file_with_invalid_input(test_client, url):
    response = test_client.post(url)
    assert response.status_code == 422

# ---------------------------------------------

# Tests for get_user_transliteration_history

def test_get_user_transliteration_history_success_auth_user(test_client, db, override_get_current_user):
   # inserting test data into test DB
    db.execute("""
        INSERT INTO transliterations (original_text, translated_text, source_language, target_language, unrecognized_symbols, created_at, status, active, user_id)
        VALUES ('Салам', 'Salam', 'az', 'az', '[]'::jsonb, NOW(), 1, True, 1)
    """)
    db.commit()

    response = test_client.get("/v1/transliteration/me/history")
    assert response.status_code == 200
    
    data = response.json()

    assert "total" in data
    assert "history" in data

    assert data["total"] == 1
    assert len(data["history"]) == 1

    item = data["history"][0]

    assert item["original_text"] == "Салам"
    assert item["result_text"] == "Salam"
    assert item["source_language"] == "az"
    assert item["target_language"] == "az"
    assert item["unrecognized_symbols"] == []
    assert item["created_at"] is not None
    assert item["status"] == 1
    assert item["active"] is True


def test_get_user_transliteration_history_auth_user_with_no_data(test_client, db, override_get_current_user):
    response = test_client.get("/v1/transliteration/me/history")
    assert response.status_code == 200
    
    data = response.json()

    assert "total" in data
    assert "history" in data

    assert data["total"] == 0
    assert len(data["history"]) == 0


def test_get_user_transliteration_history_not_auth_user(test_client, db):
    response = test_client.get("/v1/transliteration/me/history")
    assert response.status_code == 401

# --------------------------------------------------------------
