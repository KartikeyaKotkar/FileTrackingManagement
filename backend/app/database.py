import sqlite3
from contextlib import contextmanager

DB_PATH = "township.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(
        DB_PATH, isolation_level=None
    )  # autocommit disabled when using BEGIN
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def create_document_with_version(
    reference_no, title, department_id, created_by, file_info
):
    """
    file_info = dict(file_name, file_path, file_hash, file_size, version_no)
    """
    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute("BEGIN;")
            cur.execute(
                "INSERT INTO document_holder (reference_no, title, department_id, created_by) VALUES (?, ?, ?, ?);",
                (reference_no, title, department_id, created_by),
            )
            doc_id = cur.lastrowid

            cur.execute(
                """INSERT INTO document_version
                           (document_id, version_no, file_name, file_path, file_hash, file_size, created_by)
                           VALUES (?, ?, ?, ?, ?, ?, ?);""",
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
            # trigger will update current_version_id automatically
            cur.execute("COMMIT;")
            return doc_id
        except Exception:
            cur.execute("ROLLBACK;")
            raise


def add_version(
    document_id, version_no, file_name, file_path, file_hash, file_size, created_by
):
    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute("BEGIN;")
            cur.execute(
                """INSERT INTO document_version
                           (document_id, version_no, file_name, file_path, file_hash, file_size, created_by)
                           VALUES (?, ?, ?, ?, ?, ?, ?);""",
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
            cur.execute("COMMIT;")
            return cur.lastrowid
        except Exception:
            cur.execute("ROLLBACK;")
            raise


def move_document(
    document_id, from_dept, to_dept, movement_type, approved_by, moved_by, remarks
):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("BEGIN;")
        cur.execute(
            """INSERT INTO document_movement
                       (document_id, from_department_id, to_department_id, movement_type, approved_by, moved_by, remarks)
                       VALUES (?, ?, ?, ?, ?, ?, ?);""",
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
            """INSERT INTO tbl_reader_log (code, log_status, log_message)
                       VALUES (?, ?, ?);""",
            (
                "DOC_TRANSFER",
                "SUCCESS",
                f"Doc {document_id} moved {from_dept}->{to_dept}",
            ),
        )
        cur.execute("COMMIT;")
