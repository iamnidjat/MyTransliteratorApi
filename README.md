# MyTransliterator (Backend — FastAPI)

**MyTransliterator** is a production-structured REST API built with FastAPI that provides Azerbaijani text transliteration with full user authentication, caching, and request logging.

---

## Features

### Transliteration
- Azerbaijani Cyrillic ↔ Latin conversion
- `.txt` file upload for batch transliteration
- Unrecognized symbol detection — returned alongside the result
- Transliteration history with pagination (authenticated users only)
- Delete single or all transliteration records

### Authentication & Security
- JWT-based auth: short-lived access token + long-lived refresh token
- Refresh token stored in `HttpOnly` cookie (not exposed to JavaScript)
- Refresh token rotation — old token invalidated on every refresh
- Soft delete on logout — tokens marked revoked, not deleted
- Optional authentication — public endpoints work without login, history saved when logged in
- Password hashing with bcrypt
- JTI blacklist — revoked tokens rejected at the dependency level *(in progress)*

### Performance & Reliability
- Redis caching on transliteration history
- Rate limiting per endpoint group: stricter on auth routes, relaxed on public routes
- Rotating file logs — separate `info.log` and `error.log`, 5 MB cap with 5 backups
- Custom business code system — every response carries a machine-readable code alongside the HTTP status
- Global exception handler — internal errors never leak stack traces to the client

### Infrastructure
- PostgreSQL via SQLAlchemy ORM
- Redis via Docker
- Fully containerized with Docker Compose (PostgreSQL + Redis + API)
- Async SQLAlchemy + aioredis replacing all synchronous DB and cache calls *(in progress)*
- GitHub Actions CI — unit tests run automatically on every push *(in progress)*

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy |
| Cache | Redis |
| Auth | JWT (python-jose) + bcrypt |
| Validation | Pydantic v2 (EmailStr, field constraints) |
| Logging | Python `logging` + RotatingFileHandler |
| Rate Limiting | slowapi |
| Containerization | Docker + Docker Compose |

---

## Installation

```bash
git clone https://github.com/iamnidjat/MyTransliterator.git
cd MyTransliterator
docker-compose up --build -d
```

To stop:
```bash
docker-compose down
```

API: [http://127.0.0.1:8080](http://127.0.0.1:8080)

Swagger docs: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)

---

## API Overview

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/v1/auth/signup` | No | Register a new user |
| POST | `/v1/auth/login` | No | Login and receive tokens |
| POST | `/v1/auth/logout` | Yes | Revoke all refresh tokens |
| POST | `/v1/auth/refresh` | Cookie | Rotate refresh token |
| POST | `/v1/auth/changepwd` | Yes | Change password |
| POST | `/v1/transliteration/az/cyrillic-to-latin` | Optional | Transliterate text |
| POST | `/v1/transliteration/az/latin-to-cyrillic` | Optional | Transliterate text |
| POST | `/v1/transliteration/az/cyrillic-to-latin/file` | Optional | Transliterate `.txt` file |
| POST | `/v1/transliteration/az/latin-to-cyrillic/file` | Optional | Transliterate `.txt` file |
| GET | `/v1/transliteration/me/history` | Yes | Get transliteration history |
| DELETE | `/v1/transliteration/me/all` | Yes | Delete all history |
| DELETE | `/v1/transliteration/me/{id}` | Yes | Delete single record |

---

## Future Plans

- Support for additional languages beyond Azerbaijani
- Upload support for Word and PDF file formats
