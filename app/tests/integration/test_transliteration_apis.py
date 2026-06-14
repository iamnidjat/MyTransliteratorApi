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
    assert item["user_id"] == 1


def test_get_user_transliteration_history_success_auth_user_custom_range(test_client, db, override_get_current_user):
    for i in range(5):
        # inserting test data into test DB
        db.execute("""
            INSERT INTO transliterations (original_text, translated_text, source_language, target_language, unrecognized_symbols, created_at, status, active, user_id)
            VALUES (original_text, translated_text, 'az', 'az', '[]'::jsonb, NOW(), 1, True, 1)
        """, {
        "original_text": f"Салам {i}",
        "translated_text": f"Salam {i}",
    })

    db.commit()

    response = test_client.get("/v1/transliteration/me/history", params={"page": 2, "page_size": 2})
    assert response.status_code == 200
    
    data = response.json()

    assert "total" in data
    assert "history" in data

    assert data["total"] == 5
    assert len(data["history"]) == 2

    item = data["history"][0]

    assert item["original_text"] == "Салам 2"
    assert item["result_text"] == "Salam 2"
    assert item["source_language"] == "az"
    assert item["target_language"] == "az"
    assert item["unrecognized_symbols"] == []
    assert item["created_at"] is not None
    assert item["status"] == 1
    assert item["active"] is True
    assert item["user_id"] == 1


def test_get_user_transliteration_history_auth_user_page_out_of_range(test_client, db, override_get_current_user):
   # inserting test data into test DB
    db.execute("""
        INSERT INTO transliterations (original_text, translated_text, source_language, target_language, unrecognized_symbols, created_at, status, active, user_id)
        VALUES ('Салам', 'Salam', 'az', 'az', '[]'::jsonb, NOW(), 1, True, 1)
    """)
    db.commit()

    response = test_client.get("/v1/transliteration/me/history", params={"page": 2, "page_size": 10})
    assert response.status_code == 200
    
    data = response.json()

    assert "total" in data
    assert "history" in data

    assert data["total"] == 1
    assert len(data["history"]) == 0

    # since the page is out of range, the history list should be empty
    assert data["history"] == []


def test_get_user_transliteration_history_auth_user_invalid_page(test_client, db, override_get_current_user):
   # inserting test data into test DB
    db.execute("""
        INSERT INTO transliterations (original_text, translated_text, source_language, target_language, unrecognized_symbols, created_at, status, active, user_id)
        VALUES ('Салам', 'Salam', 'az', 'az', '[]'::jsonb, NOW(), 1, True, 1)
    """)
    db.commit()

    response = test_client.get("/v1/transliteration/me/history", params={"page": 0, "page_size": 10})
    assert response.status_code == 422


def test_get_user_transliteration_history_auth_user_invalid_page_size(test_client, db, override_get_current_user):
   # inserting test data into test DB
    db.execute("""
        INSERT INTO transliterations (original_text, translated_text, source_language, target_language, unrecognized_symbols, created_at, status, active, user_id)
        VALUES ('Салам', 'Salam', 'az', 'az', '[]'::jsonb, NOW(), 1, True, 1)
    """)
    db.commit()

    response = test_client.get("/v1/transliteration/me/history", params={"page": 1, "page_size": 1000})
    assert response.status_code == 422


def test_get_user_transliteration_history_user_isolation(test_client, db, override_get_current_user):
    # USER A data
    db.execute("""
        INSERT INTO transliterations
        (original_text, translated_text, source_language, target_language,
         unrecognized_symbols, created_at, status, active, user_id)
        VALUES ('A1', 'A1', 'az', 'az', '[]'::jsonb, NOW(), 1, True, 1)
    """)

    # USER B data
    db.execute("""
        INSERT INTO transliterations
        (original_text, translated_text, source_language, target_language,
         unrecognized_symbols, created_at, status, active, user_id)
        VALUES ('B1', 'B1', 'az', 'az', '[]'::jsonb, NOW(), 1, True, 2)
    """)

    db.commit()

    response = test_client.get("/v1/transliteration/me/history")
    assert response.status_code == 200

    data = response.json()

    # for user.id = 1
    assert data["total"] == 1
    assert len(data["history"]) == 1

    assert data["history"][0]["original_text"] == "A1"


def test__get_user_transliteration_history_filters_inactive_records(test_client, db, override_get_current_user):
    db.execute("""
        INSERT INTO transliterations
        (original_text, translated_text, source_language, target_language,
         unrecognized_symbols, created_at, status, active, user_id)
        VALUES ('ACTIVE', 'ACTIVE', 'az', 'az', '[]'::jsonb, NOW(), 1, True, 1)
    """)

    db.execute("""
        INSERT INTO transliterations
        (original_text, translated_text, source_language, target_language,
         unrecognized_symbols, created_at, status, active, user_id)
        VALUES ('INACTIVE', 'INACTIVE', 'az', 'az', '[]'::jsonb, NOW(), 1, False, 1)
    """)

    db.commit()

    response = test_client.get("/v1/transliteration/me/history")
    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["history"]) == 1

    assert data["history"][0]["original_text"] == "ACTIVE"
    assert "INACTIVE" not in [x["original_text"] for x in data["history"]]


def test_get_user_transliteration_history_auth_user_with_no_data(test_client, override_get_current_user):
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

# Tests for delete_transliteration_history

def test_delete_transliteration_history_success_auth_user(test_client, db, override_get_current_user):
    # inserting test data into test DB
    db.execute("""
        INSERT INTO transliterations (original_text, translated_text, source_language, target_language, unrecognized_symbols, created_at, status, active, user_id)
        VALUES ('Салам', 'Salam', 'az', 'az', '[]'::jsonb, NOW(), 1, True, 1)
    """)
    db.commit()

    response = test_client.delete("/v1/transliteration/me/all")
    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert "done_at" in data["data"]
    assert "status" in data["data"]
    assert "user_id" in data["data"]

    assert data["data"]["done_at"] is not None
    assert data["data"]["status"] == 1
    assert data["data"]["user_id"] == 1

    row = db.execute("SELECT * FROM transliterations WHERE user_id = 1").fetchall()
    assert len(row) == 0 


def test_delete_transliteration_history_auth_user_with_no_data(test_client, db, override_get_current_user):
    response = test_client.delete("/v1/transliteration/me/all")
    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert "done_at" in data["data"]
    assert "status" in data["data"]
    assert "user_id" in data["data"]

    assert data["data"]["done_at"] is not None
    assert data["data"]["status"] == 1
    assert data["data"]["user_id"] == 1

    row = db.execute("SELECT * FROM transliterations WHERE user_id = 1").fetchall()
    assert len(row) == 0 


def test_delete_transliteration_history_non_auth_user(test_client):
    response = test_client.delete("/v1/transliteration/me/all")
    assert response.status_code == 401


def test_delete_transliteration_history_other_users_data(test_client, db, override_get_current_user):
    # inserting record for another user (user_id = 2)
    db.execute("""
        INSERT INTO transliterations (
            original_text, translated_text, source_language,
            target_language, unrecognized_symbols,
            created_at, status, active, user_id
        )
        VALUES ('Салам', 'Salam', 'az', 'az', '[]'::jsonb, NOW(), 1, True, 2)
    """)
    db.commit()

    # override_get_current_user will return user with id 1, but the record belongs to user with id 2, so it should return 404
    response = test_client.delete("/v1/transliteration/me/all")
    assert response.status_code == 404

# --------------------------------------------------------------

# Tests for delete_single_transliteration

def test_delete_single_transliteration_success_auth_user(test_client, db, override_get_current_user):
    # inserting test data into test DB
    db.execute("""
        INSERT INTO transliterations (original_text, translated_text, source_language, target_language, unrecognized_symbols, created_at, status, active, user_id)
        VALUES ('Салам', 'Salam', 'az', 'az', '[]'::jsonb, NOW(), 1, True, 1)
    """)
    db.commit()

    response = test_client.delete("/v1/transliteration/me/1")
    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert "original_text" in data["data"]
    assert "result_text" in data["data"]
    assert "unrecognized_symbols" in data["data"]
    assert "done_at" in data["data"]
    assert "status" in data["data"]
    assert "user_id" in data["data"]

    assert data["data"]["original_text"] == "Салам"
    assert data["data"]["result_text"] == "Salam"
    assert data["data"]["unrecognized_symbols"] == []
    assert data["data"]["done_at"] is not None
    assert data["data"]["status"] == 1
    assert data["data"]["user_id"] == 1

    row = db.execute("SELECT * FROM transliterations WHERE user_id = 1").fetchall()
    assert len(row) == 0 


def test_delete_single_transliteration_auth_user_with_no_data(test_client, override_get_current_user):
    response = test_client.delete("/v1/transliteration/me/1")
    assert response.status_code == 404


def test_delete_single_transliteration_non_auth_user(test_client):
    response = test_client.delete("/v1/transliteration/me/1")
    assert response.status_code == 401


def test_delete_single_transliteration_other_users_data(test_client, db, override_get_current_user):
    # inserting record for another user (user_id = 2)
    db.execute("""
        INSERT INTO transliterations (
            original_text, translated_text, source_language,
            target_language, unrecognized_symbols,66
            created_at, status, active, user_id
        )
        VALUES ('Салам', 'Salam', 'az', 'az', '[]'::jsonb, NOW(), 1, True, 2)
    """)
    db.commit()

    # override_get_current_user will return user with id 1, but the record belongs to user with id 2, so it should return 404
    response = test_client.delete("/v1/transliteration/me/1")
    assert response.status_code == 404