# gruhoe-db

A Flask web app for searching and analysing a personal log of daily album picks
("Gruhö" is short for "Gruppenhören", "listen together").
Picks are kept in Google Docs, synced into a PostgreSQL database, and can then be searched, exported and visualised.

## Features

- **Search** picks by artist/album text and by date range, rendered as HTML or exported as JSON or CSV.
- **Statistics** page with charts of picks per month (all time and current year) and per weekday.
- **Sync** new picks from one or more Google Docs into the database (password-protected in the UI).

## Project layout

| Path | Purpose |
| --- | --- |
| `gruhoedb/webserver.py` | Flask app and routes |
| `gruhoedb/repos.py` | `PickRepository` (PostgreSQL) and `GoogleDocsRepo` (Google Docs parser) |
| `gruhoedb/services.py` | `SyncService` and its factory |
| `gruhoedb/credentials.py` | Google service account credentials (from file or env vars) |
| `gruhoedb/models.py` | `Pick` and `StatsEntry` models |
| `gruhoedb/templates/`, `gruhoedb/static/` | HTML templates and front-end assets |
| `create-schema.sql` | Database schema |

## Routes

| Route | Description |
| --- | --- |
| `GET /` | Search form |
| `GET /search?query=&from=&to=&outputformat=html\|json\|csv` | Search picks. `from`/`to` are ISO dates (`YYYY-MM-DD`); `outputformat` is required |
| `GET /stats` | Statistics charts |
| `POST /login` | Checks the `password` form field against `ADMIN_PASSWORD` and, on success, marks the session as authenticated |
| `GET /newpicks` | Lists picks found in the Google Docs that are not yet synced (requires login, else `401`) |
| `POST /sync` | Writes the new picks to the database (requires login, else `401`) |

Month and weekday names are localised using the browser's `Accept-Language` header (falls back to `en`).

## Google Docs format

The sync parser expects each document to be structured with these paragraph styles:

- **Title**: contains the year (e.g. `Gruhö 2024`)
- **Heading 1**: the month name, in the request locale (e.g. `März`)
- **Heading 2**: the day of month followed by a dot (e.g. `17.`)
- **Normal text**: one pick per line, as `Artist - Album`

## Setup

Requires Python 3 and a PostgreSQL database.

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create the table using `create-schema.sql` (the schema `dbo` is expected inside the database named by `DB_NAME`).

### Configuration

Configuration is read from environment variables. `flask run` (`make localdebug`) loads a `.env` file automatically via `python-dotenv`; for gunicorn (`make local`), export the variables yourself, e.g. `set -a; source .env; set +a`.

| Variable | Description |
| --- | --- |
| `DB_CONNECTION` | PostgreSQL connection string |
| `DB_NAME` | Database name, used to qualify the `picks` table |
| `FLASK_SECRET_KEY` | Flask secret key, used to sign the session cookie (required for login) |
| `ADMIN_PASSWORD` | Password checked by `/login` |
| `GOOGLE_DOCUMENT_IDS` | Google Doc IDs to sync, separated by `;` |
| `GOOGLE_SERVICE_ACCOUNT_EMAIL` | Service account fields, as found in the service account JSON key: |
| `GOOGLE_SERVICE_ACCOUNT_CLIENT_ID` | |
| `GOOGLE_SERVICE_ACCOUNT_KEY` | (`private_key`) |
| `GOOGLE_SERVICE_ACCOUNT_KEY_ID` | |
| `GOOGLE_SERVICE_ACCOUNT_PROJECT_ID` | |
| `GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL` | |
| `GOOGLE_SERVICE_ACCOUNT_TOKEN_URI` | |

Share each Google Doc with the service account's email address so it can read it. Never commit `.env` or the service account JSON (`*.json` is git-ignored).

## Running

```sh
make local        # gunicorn on http://127.0.0.1:8080
make localdebug   # Flask dev server with debug/reload
```

## Docker

```sh
make build        # builds thatisfine/gruhoedb:<git describe>
make push         # pushes the image
docker run -p 8080:8080 --env-file .env thatisfine/gruhoedb:<version>
```

The container listens on the port given by `PORT` (default `8080`).

## Development

```sh
pip install -r requirements-dev.txt   # flake8, pytest
flake8
pytest
```

Most tests run without any external services. The `PickRepository` tests need a PostgreSQL database and are skipped
unless `TEST_DB_CONNECTION` is set. Use an **empty** database named `gruhoedb` (the name is hard-coded in
`create-schema.sql`); the tests create `dbo.picks` and drop it again, and refuse to run if that table already exists.

```sh
docker run -d --rm -p 5432:5432 -e POSTGRES_PASSWORD=test -e POSTGRES_DB=gruhoedb postgres:17
TEST_DB_CONNECTION=postgresql://postgres:test@localhost:5432/gruhoedb pytest
```

### CI

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every pull request and on pushes to `main`:

1. **test**: `flake8` and `pytest` against a PostgreSQL service container.
2. **docker**: builds the image and smoke-tests that the container serves `GET /`.
