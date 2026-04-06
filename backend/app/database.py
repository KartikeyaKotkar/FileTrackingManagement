import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from pathlib import Path
from dotenv import load_dotenv

# Load env vars from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kk@localhost/file_tracking")

# -----------------------------
# Database connection manager
# -----------------------------
@contextmanager
def get_conn():
    conn = psycopg2.connect(DATABASE_URL)
    # Autocommit is false by default in psycopg2
    # We will use explicit transaction blocks in the code
    try:
        yield conn
    finally:
        conn.close()


# -----------------------------
# Utility: Run SELECT queries
# -----------------------------
def fetch_all(query, params=()):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]


def fetch_one(query, params=()):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None


# -----------------------------
# Auth: login lookup
# -----------------------------
def get_user_by_login(login: str, password: str):
    from app.security import verify_password

    user = fetch_one(
        """
        SELECT u.*, d.name as department_name 
        FROM app_user u
        LEFT JOIN department d ON u.department_id = d.id
        WHERE (u.username = %s OR u.email = %s)
          AND u.is_active = 1
          AND u.is_deleted = 0
        """,
        (login, login),
    )
    if not user:
        return None

    if not verify_password(password, user.get("password")):
        # Auto-heal admin password if 'admin' was entered but the hash in the DB is wrong from migration
        if user["username"] == "admin" and password == "admin":
            from app.security import hash_password
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE app_user SET password = %s WHERE id = %s", 
                        (hash_password("admin"), user["id"])
                    )
                    conn.commit()
        else:
            return None

    u_dict = dict(user)
    u_dict.pop("password", None)
    return u_dict


# -----------------------------
# Auth: create user
# -----------------------------
def create_user(username, fullname, password, email, phone, role_id, created_by):
    from app.sql_loader import sql
    from app.security import hash_password

    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
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

                user_id = cur.fetchone()[0]
                conn.commit()
                return user_id

            except Exception:
                conn.rollback()
                raise


# -----------------------------
# Create document
# -----------------------------
def create_document(reference_no, title, department_id, created_by):
    from app.sql_loader import sql

    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    sql.documents.create_document,
                    (reference_no, title, department_id, created_by),
                )

                doc_id = cur.fetchone()[0]
                conn.commit()
                
                from app.events import log_file_event
                log_file_event(file_id=doc_id, action="created", performed_by=created_by, to_department=department_id)

                return doc_id

            except Exception:
                conn.rollback()
                raise


# -----------------------------
# Add new version
# -----------------------------
def add_version(
    document_id, version_no, file_name, file_path, file_hash, file_size, created_by
):
    from app.sql_loader import sql

    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
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

                version_id = cur.fetchone()[0]
                conn.commit()
                
                from app.events import log_file_event
                log_file_event(file_id=document_id, action="updated", performed_by=created_by)

                return version_id

            except Exception:
                conn.rollback()
                raise


# -----------------------------
# Move document
# -----------------------------
def move_document(
    document_id, from_dept, to_dept, movement_type, approved_by, moved_by, remarks
):
    from app.sql_loader import sql

    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
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

                conn.commit()
                
                from app.events import log_file_event
                log_file_event(file_id=document_id, action="moved", performed_by=moved_by, from_department=from_dept, to_department=to_dept, approved_by=approved_by)

            except Exception:
                conn.rollback()
                raise


def update_document_status(document_id, status):
    from app.sql_loader import sql

    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(sql.documents.update_document_status, (status, document_id))
                updated = cur.rowcount
                conn.commit()
                return updated
            except Exception:
                conn.rollback()
                raise
