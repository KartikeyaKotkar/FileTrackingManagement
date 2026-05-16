from app.database import get_conn

def init_events_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS file_event (
                    id SERIAL PRIMARY KEY,
                    file_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    from_department INTEGER,
                    to_department INTEGER,
                    performed_by INTEGER,
                    approved_by INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES document_holder (id),
                    FOREIGN KEY (performed_by) REFERENCES app_user (id),
                    FOREIGN KEY (from_department) REFERENCES department (id),
                    FOREIGN KEY (to_department) REFERENCES department (id),
                    FOREIGN KEY (approved_by) REFERENCES app_user (id)
                )
            """)
            conn.commit()
            
    # Auto-repair sequences from SQLite-to-Postgres manual insertions using dynamic sequence fetching
    tables = [
        "department",
        "role",
        "app_user",
        "document_holder",
        "document_movement",
        "document_version",
        "file_event",
        "transfer_request",
        "tbl_reader_log"
    ]
    for table in tables:
        try:
            with get_conn() as reset_conn:
                with reset_conn.cursor() as reset_cur:
                    # Dynamically get the exact sequence name for the column 'id'
                    reset_cur.execute(f"SELECT pg_get_serial_sequence('{table}', 'id');")
                    seq_name = reset_cur.fetchone()[0]
                    if seq_name:
                        reset_cur.execute(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX(id) FROM {table}), 1));")
                    reset_conn.commit()
        except Exception:
            try:
                reset_conn.rollback()
            except Exception:
                pass



def log_file_event(file_id: int, action: str, performed_by: int, from_department: int = None, to_department: int = None, approved_by: int = None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO file_event (file_id, action, from_department, to_department, performed_by, approved_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (file_id, action, from_department, to_department, performed_by, approved_by))
            conn.commit()
