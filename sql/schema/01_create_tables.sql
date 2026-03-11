PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- Departments (if not present in older schema)
CREATE TABLE IF NOT EXISTS department (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Users (basic)
CREATE TABLE IF NOT EXISTS app_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    fullname TEXT,
    role TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Master document table (metadata)
CREATE TABLE IF NOT EXISTS document_holder (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_no TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    department_id INTEGER NOT NULL DEFAULT 1,
    current_version_id INTEGER,        -- maintained by trigger; not FK-ed to avoid circular creation issues
    status TEXT NOT NULL DEFAULT 'Active',
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(department_id) REFERENCES department(id) ON DELETE RESTRICT,
    FOREIGN KEY(created_by) REFERENCES app_user(id) ON DELETE SET NULL
    -- Add to document_holder table:
    current_holder_user_id INTEGER,          -- who physically has the file
    current_holder_department_id INTEGER,    -- which dept currently holds it (not owns it)
    last_movement_id INTEGER,               -- denormalized for fast lookup
    status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Open', 'Active', 'Closed')),

    FOREIGN KEY(current_holder_user_id) REFERENCES app_user(id),
    FOREIGN KEY(current_holder_department_id) REFERENCES department(id),
    FOREIGN KEY(last_movement_id) REFERENCES document_movement(id)
);

-- Document versions (one-to-many)
CREATE TABLE IF NOT EXISTS document_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    version_no INTEGER NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_hash TEXT,
    file_size INTEGER,
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Active',
    FOREIGN KEY(document_id) REFERENCES document_holder(id) ON DELETE CASCADE,
    FOREIGN KEY(created_by) REFERENCES app_user(id) ON DELETE SET NULL,
    UNIQUE(document_id, version_no)
);

-- Movement / Transfer history
CREATE TABLE IF NOT EXISTS document_movement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    from_department_id INTEGER,
    to_department_id INTEGER,
    movement_type TEXT DEFAULT 'Transfer',
    approved_by INTEGER,
    moved_by INTEGER,
    moved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    FOREIGN KEY(document_id) REFERENCES document_holder(id) ON DELETE CASCADE,
    FOREIGN KEY(from_department_id) REFERENCES department(id),
    FOREIGN KEY(to_department_id) REFERENCES department(id),
    FOREIGN KEY(approved_by) REFERENCES app_user(id),
    FOREIGN KEY(moved_by) REFERENCES app_user(id)
);

-- Reader / hardware log table (as in your senior schema)
CREATE TABLE IF NOT EXISTS tbl_reader_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT,
    log_datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    log_status TEXT,
    log_message TEXT
);

-- Indexes to speed queries
CREATE INDEX IF NOT EXISTS idx_document_department ON document_holder(department_id);
CREATE INDEX IF NOT EXISTS idx_document_reference ON document_holder(reference_no);
CREATE INDEX IF NOT EXISTS idx_version_document ON document_version(document_id);
CREATE INDEX IF NOT EXISTS idx_movement_document ON document_movement(document_id);
CREATE INDEX IF NOT EXISTS idx_reader_log_code ON tbl_reader_log(code, log_datetime);

-- Trigger: update document_holder.current_version_id when a new version inserted,
-- only if the new version_no is greater or current is NULL.
CREATE TRIGGER IF NOT EXISTS trg_update_current_version_after_insert
AFTER INSERT ON document_version
BEGIN
  UPDATE document_holder
  SET current_version_id = NEW.id
  WHERE id = NEW.document_id
    AND (
       current_version_id IS NULL
       OR NEW.version_no >= COALESCE(
           (SELECT version_no FROM document_version WHERE id = current_version_id),
           0
       )
    );
END;

-- Optional: audit trigger to log version insertions into tbl_reader_log
CREATE TRIGGER IF NOT EXISTS trg_log_version_insert
AFTER INSERT ON document_version
BEGIN
  INSERT INTO tbl_reader_log(code, log_status, log_message)
  VALUES('DOC_VERSION_ADD', 'SUCCESS', 'Added version ' || NEW.version_no || ' for doc_id=' || NEW.document_id);
END;

CREATE TRIGGER IF NOT EXISTS trg_update_holder_after_movement
AFTER INSERT ON document_movement
BEGIN
  UPDATE document_holder
  SET
    current_holder_department_id = NEW.to_department_id,
    current_holder_user_id = NEW.moved_by,
    last_movement_id = NEW.id
  WHERE id = NEW.document_id;
END;
