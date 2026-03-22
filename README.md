# MyTransliterator (Backend - FastAPI)

**MyTransliterator** is a backend API built with FastAPI that provides text transliteration services.

---

## Features

* **Transliteration:** Azerbaijani Cyrillic ↔ Latin
* **User Authentication:** signup, login, logout
* **TXT File Upload:** users can upload `.txt` files for transliteration
* **Transliteration History:** retrieve user transliteration history
* **Manage Transliterations:** ability to remove saved transliterations
* **Logging:** request and system activity logging implemented
* **Performance Optimization:** Redis caching used to improve API speed
* **Containerization:** Docker support for easy deployment
* Returns unrecognized symbols in transliteration
* Designed for future expansion to support other languages and scripts

---

## Installation

```bash
git clone https://github.com/iamnidjat/MyTransliterator.git
cd MyTransliterator
docker-compose up --build -d
To stop the app: docker-compose down
```

API available at:
[http://127.0.0.1:8000](http://127.0.0.1:8080)

Swagger docs:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8080/docs)

---

## Future Plans

* Support for more languages (beyond Azerbaijani)
* Upload support for additional file formats (Word, PDF)
* Full API documentation improvements
* Enhanced API responses
