# Smart Campus – Vue + Django + PostgreSQL

## Folder placement

Extract this folder into your repository at `Assignments/Assignment3/`. The resulting layout should be:

```text
Assignment3/
├── backend/                 # Existing Django project goes here
│   ├── manage.py
│   ├── config/
│   ├── campus/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
├── docker-compose.yml
├── .env.example
└── README-DOCKER.md
```

**Important:** The backend Dockerfile expects the Django project (`manage.py`, `config/`, and `campus/`) to be inside `backend/`. Keep the backend files from the previous code package in that folder.

## Start the application

1. Install Docker Desktop and start it.
2. Copy `.env.example` to `.env`.
3. Change `SECRET_KEY` and `DB_PASSWORD` in `.env`.
4. From the `Assignment3` folder, run:

```bash
docker compose up --build
```

5. Open:
   - Vue frontend: http://localhost:5173
   - Django API: http://localhost:8000/api/
   - Django admin: http://localhost:8000/admin/

## Create an admin user

Open another terminal in `Assignment3`:

```bash
docker compose exec backend python manage.py createsuperuser
```

Use the created account to sign in to Django admin and add facilities.

## Stop

```bash
docker compose down
```

To stop and also delete the database volume (this permanently deletes local database data):

```bash
docker compose down -v
```

## PostgreSQL configuration

The compose file creates a PostgreSQL 16 database. Database data is stored in the named `postgres_data` volume and remains after normal container restarts.

## Backend settings required

Update `backend/config/settings.py` to read PostgreSQL environment variables. Replace the existing SQLite `DATABASES` setting with:

```python
import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "smartcampus"),
        "USER": os.getenv("DB_USER", "campus_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
```

For local development, add `localhost,127.0.0.1` to `ALLOWED_HOSTS`. In Docker, the environment file includes `backend`.

Ensure the backend requirements include `psycopg[binary]` and `gunicorn`.

## Notes

- This is a development configuration, not a production deployment.
- The frontend uses Django session authentication conventions; the login page is a simple starter and may need adjustment to match the exact backend authentication setup.
- Configure CSRF trusted origins and secure cookies before deployment behind HTTPS.
- The booking overlap check in the earlier starter backend is an application-level check. For race-safe simultaneous booking, add a PostgreSQL exclusion constraint or transactional locking before claiming concurrency safety.
- Do not use the example database password in a public deployment.
