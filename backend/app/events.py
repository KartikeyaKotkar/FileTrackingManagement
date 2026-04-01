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

def log_file_event(file_id: int, action: str, performed_by: int, from_department: int = None, to_department: int = None, approved_by: int = None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO file_event (file_id, action, from_department, to_department, performed_by, approved_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (file_id, action, from_department, to_department, performed_by, approved_by))
            conn.commit()
