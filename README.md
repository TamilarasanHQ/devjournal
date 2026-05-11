
# DevJournal API

A personal developer journal backend built with **FastAPI** and **PostgreSQL**, featuring JWT authentication, tagging, full-text search, pagination, and a **spaced repetition review scheduler**.

---

## 🚀 Features

- **User registration** with hashed passwords (PBKDF2-SHA256)
- **JWT authentication** (access tokens, protected routes)
- **Journal entries**: create, read, update, delete (user‑scoped)
- **Tags**: many‑to‑many relationship, filter entries by tag
- **Search & pagination**: search in title/content with `skip`/`limit`
- **Spaced repetition**: rate your understanding (1‑5), API tracks review history and calculates next review date
- **Automated tests** (24 endpoint tests using `pytest`)

---

## 🧱 Tech Stack

- **FastAPI** (Python web framework)
- **PostgreSQL** (database)
- **SQLAlchemy** (ORM)
- **psycopg2** (PostgreSQL driver)
- **python-jose** (JWT)
- **python-dotenv** (environment variables)
- **pytest** + **httpx** (testing)

---

## 📦 Setup

### Prerequisites

- Python 3.10+
- PostgreSQL installed and running
- `psql` or pgAdmin access

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd devjournal-backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

*(If you don’t have a `requirements.txt`, you can generate one with `pip freeze > requirements.txt`.)*

### 4. Create the database
In PostgreSQL (using pgAdmin or `psql`):
```sql
CREATE DATABASE devjournal;
```

### 5. Set up environment variables
Copy the example file and fill in your real credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_NAME=devjournal
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🏃 Running the App

Start the development server:
```bash
uvicorn main:app --reload
```

API available at [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Interactive docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
ReDoc at [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📚 API Endpoints

### Health
| Method | Endpoint    | Description         |
|--------|-------------|---------------------|
| GET    | `/`         | API status          |
| GET    | `/health`   | Database connection check |

### Authentication
| Method | Endpoint          | Description                |
|--------|-------------------|----------------------------|
| POST   | `/users/register` | Create a new user          |
| POST   | `/token`          | Login, receive JWT token   |

### Entries *(all require Bearer token)*
| Method | Endpoint                         | Description                                      |
|--------|----------------------------------|--------------------------------------------------|
| POST   | `/entries`                       | Create an entry (optional tags)                  |
| GET    | `/entries`                       | List own entries (search, tag filter, pagination)|
| GET    | `/entries/due_for_review`        | Entries ready for review (spaced repetition)     |
| GET    | `/entries/{id}`                  | Get a single entry                               |
| PUT    | `/entries/{id}`                  | Update title, content, tags                      |
| DELETE | `/entries/{id}`                  | Delete an entry                                  |
| POST   | `/entries/{id}/review`           | Submit a review rating (1‑5)                     |

**Query parameters for `GET /entries`:**  
`search` – keyword in title or content  
`tag` – filter by tag name  
`skip` – pagination offset (default 0)  
`limit` – page size (default 10, max 100)

### Tags *(require Bearer token)*
| Method | Endpoint | Description     |
|--------|----------|-----------------|
| POST   | `/tags`  | Create a new tag|
| GET    | `/tags`  | List all tags   |

---

## 🧪 Running Tests

1. Create a **separate test database** in PostgreSQL:
   ```sql
   CREATE DATABASE devjournal_test;
   ```

2. Create a `.env.test` file with the same variables but `DATABASE_NAME=devjournal_test`.

3. Run the tests:
   ```bash
   pytest tests/ -v
   ```

Currently **24 tests** covering health, auth, entries, tags, and reviews all pass.

---

## 📂 Project Structure

```
devjournal-backend/
├── main.py           # FastAPI app, all endpoints
├── models.py         # SQLAlchemy models (User, Entry, Tag, EntryTag)
├── schemas.py        # Pydantic schemas
├── database.py       # Database connection, engine, Base
├── auth.py           # JWT token creation, get_current_user
├── utils.py          # Password hashing, spaced repetition logic
├── .env              # Environment variables (ignored by Git)
├── .env.test         # Test database variables (ignored)
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── tests/
    ├── conftest.py       # Test fixtures, test database setup
    ├── test_health.py
    ├── test_auth.py
    ├── test_entries.py
    ├── test_tags.py
    └── test_review.py
```

---

## 📝 License

This project is open‑source and available under the [MIT License](LICENSE) (optional – add if you like).

---

## 🙌 Acknowledgements

Built as a learning project following a structured phase‑by‑phase plan covering API development, authentication, ORM, and testing.
```
