import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = "main.db"


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
# Utility: Load SQL files
# -----------------------------
def load_query(path: str):
    return Path(path).read_text()


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

    return fetch_one(
        sql.users.get_user_by_login,
        (login, login, password),  # login passed twice: for username + email check
    )


# -----------------------------
# Auth: create user
# -----------------------------
def create_user(username, fullname, password, email, phone, role_id, created_by):
    from app.sql_loader import sql

    with get_conn() as conn:
        cur = conn.cursor()

        try:
            cur.execute("BEGIN")

            cur.execute(
                sql.users.create_user,
                (username, fullname, password, email, phone, role_id, created_by),
            )

            user_id = cur.lastrowid
            cur.execute("COMMIT")
            return user_id

        except Exception:
            cur.execute("ROLLBACK")
            raise


# -----------------------------
# Create document + first version
# -----------------------------
def create_document_with_version(
    reference_no, title, department_id, created_by, file_info
):
    """
    file_info = {
        "version_no": int,
        "file_name": str,
        "file_path": str,
        "file_hash": str,
        "file_size": int
    }
    """

    with get_conn() as conn:
        cur = conn.cursor()

        try:
            cur.execute("BEGIN")

            cur.execute(
                """
                INSERT INTO document_holder
                (reference_no, title, department_id, created_by)
                VALUES (?, ?, ?, ?)
                """,
                (reference_no, title, department_id, created_by),
            )

            doc_id = cur.lastrowid

            cur.execute(
                """
                INSERT INTO document_version
                (document_id, version_no, file_name, file_path, file_hash, file_size, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc_id,
                    file_info["version_no"],
                    file_info["file_name"],
                    file_info["file_path"],
                    file_info.get("file_hash"),
                    file_info.get("file_size"),
                    created_by,
                ),
            )

            cur.execute("COMMIT")
            return doc_id

        except Exception:
            cur.execute("ROLLBACK")
            raise


# -----------------------------
# Add new version
# -----------------------------
def add_version(
    document_id, version_no, file_name, file_path, file_hash, file_size, created_by
):

    with get_conn() as conn:
        cur = conn.cursor()

        try:
            cur.execute("BEGIN")

            cur.execute(
                """
                INSERT INTO document_version
                (document_id, version_no, file_name, file_path, file_hash, file_size, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
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

    with get_conn() as conn:
        cur = conn.cursor()

        try:
            cur.execute("BEGIN")

            cur.execute(
                """
                INSERT INTO document_movement
                (document_id, from_department_id, to_department_id, movement_type,
                approved_by, moved_by, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
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
                """
                INSERT INTO tbl_reader_log (code, log_status, log_message)
                VALUES (?, ?, ?)
                """,
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
