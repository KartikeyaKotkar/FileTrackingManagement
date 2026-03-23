import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "SQL" / "main.db"


# -----------------------------
# Database connection manager
# -----------------------------
@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    finally:
        conn.close()


# -----------------------------
# Utility: Run SELECT queries
# -----------------------------
def fetch_all(query, params=()):
    with get_conn() as conn:
        cur = conn.cursor()
        rows = cur.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def fetch_one(query, params=()):
    with get_conn() as conn:
        cur = conn.cursor()
        row = cur.execute(query, params).fetchone()
        return dict(row) if row else None


# -----------------------------
# Auth: login lookup
# -----------------------------
def get_user_by_login(login: str, password: str):
    """
    Matches username OR email + password.
    Returns user dict (without password) or None.
    """
    from app.sql_loader import sql
    from app.security import verify_password

    # --- TEMPORARY ADMIN BYPASS ---
    if login == "admin" and password == "admin":
        user = fetch_one(sql.users.get_user_by_login, ("admin", "admin"))
        if user:
            u_dict = dict(user)
            u_dict.pop("password", None)
            return u_dict
    # ------------------------------

    user = fetch_one(
        sql.users.get_user_by_login,
        (login, login),  # login passed twice: for username + email check
    )
    if not user or not verify_password(password, user.get("password")):
        return None

    user.pop("password", None)
    return user


# -----------------------------
# Auth: create user
# -----------------------------
def create_user(username, fullname, password, email, phone, role_id, created_by):
    from app.sql_loader import sql
    from app.security import hash_password

    with get_conn() as conn:
        cur = conn.cursor()

        try:
            cur.execute("BEGIN")

            cur.execute(
                sql.users.create_user,
                (
                    username,
                    fullname,
                    hash_password(password),
                    email,
                    phone,
                    role_id,
                    created_by,
                ),
            )

            user_id = cur.lastrowid
            cur.execute("COMMIT")
            return user_id

        except Exception:
            cur.execute("ROLLBACK")
            raise


# -----------------------------
# Create document
# -----------------------------
def create_document(reference_no, title, department_id, created_by):
    from app.sql_loader import sql

    with get_conn() as conn:
        cur = conn.cursor()

        try:
            cur.execute("BEGIN")

            cur.execute(
                sql.documents.create_document,
                (reference_no, title, department_id, created_by),
            )

            cur.execute("COMMIT")
            return cur.lastrowid

        except Exception:
            cur.execute("ROLLBACK")
            raise


# -----------------------------
# Add new version
# -----------------------------
def add_version(
    document_id, version_no, file_name, file_path, file_hash, file_size, created_by
):
    from app.sql_loader import sql

    with get_conn() as conn:
        cur = conn.cursor()

        try:
            cur.execute("BEGIN")

            cur.execute(
                sql.versions.create_version,
                (
                    document_id,
                    version_no,
                    file_name,
                    file_path,
                    file_hash,
                    file_size,
                    created_by,
                ),
            )

            cur.execute("COMMIT")
            return cur.lastrowid

        except Exception:
            cur.execute("ROLLBACK")
            raise


# -----------------------------
# Move document
# -----------------------------
def move_document(
    document_id, from_dept, to_dept, movement_type, approved_by, moved_by, remarks
):
    from app.sql_loader import sql

    with get_conn() as conn:
        cur = conn.cursor()

        try:
            cur.execute("BEGIN")

            cur.execute(
                sql.movement.move_document,
                (
                    document_id,
                    from_dept,
                    to_dept,
                    movement_type,
                    approved_by,
                    moved_by,
                    remarks,
                ),
            )

            cur.execute(
                sql.logs.insert_log,
                (
                    "DOC_TRANSFER",
                    "SUCCESS",
                    f"Doc {document_id} moved {from_dept}->{to_dept}",
                ),
            )

            cur.execute("COMMIT")

        except Exception:
            cur.execute("ROLLBACK")
            raise


def update_document_status(document_id, status):
    from app.sql_loader import sql

    with get_conn() as conn:
        cur = conn.cursor()

        try:
            cur.execute("BEGIN")
            cur.execute(sql.documents.update_document_status, (status, document_id))
            updated = cur.rowcount
            cur.execute("COMMIT")
            return updated
        except Exception:
            cur.execute("ROLLBACK")
            raise
