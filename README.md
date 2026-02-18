# MyTransliterator (Backend - FastAPI)

**MyTransliterator** is a backend API built with **FastAPI** that provides text transliteration services.

---

## Features

- Transliteration: Azerbaijani **Cyrillic ↔ Latin**
- User authentication: **signup, login, logout**
- Designed for **future expansion**: other languages and scripts
- Returns **unrecognized symbols** in transliteration

---

## Installation

```bash
git clone https://github.com/iamnidjat/MyTransliterator.git
cd MyTransliterator
python -m venv venv
# activate venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API available at: http://127.0.0.1:8000

Swagger docs: http://127.0.0.1:8000/docs

# Future Plans

More languages (beyond Azerbaijani)

File uploads

Enhanced API responses