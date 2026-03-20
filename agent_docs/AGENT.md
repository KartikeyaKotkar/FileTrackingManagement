# File Tracking System — AI AGENT Context

Enterprise document management backend for a government office.
FastAPI + SQLite, single-machine offline deployment.

## Stack

- **Backend**: FastAPI (Python), Uvicorn
- **DB**: SQLite via raw `sqlite3` — no ORM, all queries in `sql/` as `.sql` files
- **Schema management**: `sql/schema/restore.sql` (fresh), `sql/schema/migrate.sql` (existing DB)
- **Package manager**: `uv`
- **Auth**: plaintext passwords (matches senior's legacy system — do not hash without approval)

## Project Layout

```
project-root/
├── AGENT.md
├── backend/
│   └── app/
│       ├── main.py          # FastAPI app, router registration
│       ├── database.py      # All DB helpers (get_conn, fetch_all, fetch_one, etc.)
│       ├── sql_loader.py    # Loads sql/**/*.sql into sql.<category>.<name>
│       ├── models/
│       │   └── schemas.py   # Pydantic request/response models
│       └── routers/
│           ├── auth.py
│           ├── documents.py
│           ├── versions.py
│           └── movement.py
└── sql/
    ├── schema/
    │   ├── restore.sql      # Full fresh build (tables + triggers + seed)
    │   └── migrate.sql      # Safe migration for existing DBs
    ├── documents/
    ├── versions/
    ├── movement/
    ├── logs/
    └── users/
```

## Commands

```bash
# Activate environment
source .venv/bin/activate

# Run server (always from backend/)
cd backend && uvicorn app.main:app --reload

# Fresh database (from project root)
sqlite3 main.db < sql/schema/restore.sql

# Add a dependency
uv pip install <package> && uv pip freeze > requirements.txt
```

## Key Rules

- The DB file `main.db` lives at project root and is referenced as `"main.db"` in `database.py` — the server must be run from `backend/` so the relative path resolves correctly
- All SQL lives in `sql/` — never inline new queries in Python files, always add a `.sql` file
- `sql_loader.py` auto-discovers `.sql` files — access via `sql.<category>.<stem>`
- `document_movement` table must be declared before `document_holder` in schema (FK dependency)
- Three triggers maintain denormalized columns automatically — do not manually update `current_version_id`, `current_holder_*`, or `last_movement_id`
- `X-Admin-Key: filetracker-admin-2025` is required for `/auth/register` and `/auth/users`
- Status field on `document_holder` is constrained to `'Open' | 'Active' | 'Closed'`

## Agent System

This project uses a structured agent system under `agent_docs/`.

### Structure

- `agents/` — agent personas (who performs the task)
- `tasks/` — task definitions (what to do)
- `context/` — project knowledge (schema, architecture, rules)
- `commands/` — preconfigured workflows (recommended entrypoints)

### Available Commands

- `commands/audit.md`
  - Runs a full backend audit using:
    - `agents/backend-auditor.md`
    - `tasks/audit.md`
    - `context/schema.md`

- `commands/docs.md`
  - Generates full project documentation after audit

### Usage

Prefer using commands instead of manually selecting files.

Example:
> Run the audit command

This ensures consistent agent + task + context composition.
