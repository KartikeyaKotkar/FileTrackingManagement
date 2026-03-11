PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ============================================================
-- TABLE: department
-- ============================================================
CREATE TABLE IF NOT EXISTS department (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL UNIQUE
);

-- ============================================================
-- TABLE: app_user
-- ============================================================
CREATE TABLE IF NOT EXISTS app_user (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT    NOT NULL UNIQUE,
    fullname   TEXT,
    role       TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: document_movement
-- Must be declared BEFORE document_holder so that
-- last_movement_id FK resolves correctly.
-- ============================================================
CREATE TABLE IF NOT EXISTS document_movement (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id        INTEGER  NOT NULL,
    from_department_id INTEGER,
    to_department_id   INTEGER,
    movement_type      TEXT     DEFAULT 'Transfer',
    approved_by        INTEGER,
    moved_by           INTEGER,
    moved_at           DATETIME DEFAULT CURRENT_TIMESTAMP,
    remarks            TEXT,
    FOREIGN KEY (document_id)        REFERENCES document_holder (id) ON DELETE CASCADE,
    FOREIGN KEY (from_department_id) REFERENCES department (id),
    FOREIGN KEY (to_department_id)   REFERENCES department (id),
    FOREIGN KEY (approved_by)        REFERENCES app_user (id),
    FOREIGN KEY (moved_by)           REFERENCES app_user (id)
);

-- ============================================================
-- TABLE: document_holder
-- Tracks ownership, current physical holder, version, status.
--
-- Columns added vs original:
--   current_holder_user_id       → who physically has the file right now
--   current_holder_department_id → which dept physically holds it (≠ owning dept)
--   last_movement_id             → denormalized FK for fast "last movement" lookup
--
-- status enforced to: 'Open' | 'Active' | 'Closed'
-- current_version_id + last_movement_id maintained by triggers (see below)
-- ============================================================
CREATE TABLE IF NOT EXISTS document_holder (
    id                           INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_no                 TEXT    NOT NULL UNIQUE,
    title                        TEXT    NOT NULL,
    department_id                INTEGER NOT NULL DEFAULT 1,   -- owning department
    current_version_id           INTEGER,                      -- → trigger: trg_update_current_version
    current_holder_user_id       INTEGER,                      -- → trigger: trg_update_holder_after_movement
    current_holder_department_id INTEGER,                      -- → trigger: trg_update_holder_after_movement
    last_movement_id             INTEGER,                      -- → trigger: trg_update_holder_after_movement
    status                       TEXT    NOT NULL DEFAULT 'Active'
                                         CHECK (status IN ('Open', 'Active', 'Closed')),
    created_by                   INTEGER,
    created_at                   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id)                REFERENCES department (id)        ON DELETE RESTRICT,
    FOREIGN KEY (created_by)                   REFERENCES app_user (id)          ON DELETE SET NULL,
    FOREIGN KEY (current_holder_user_id)       REFERENCES app_user (id),
    FOREIGN KEY (current_holder_department_id) REFERENCES department (id),
    FOREIGN KEY (last_movement_id)             REFERENCES document_movement (id)
);

-- ============================================================
-- TABLE: document_version
-- ============================================================
CREATE TABLE IF NOT EXISTS document_version (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER  NOT NULL,
    version_no  INTEGER  NOT NULL,
    file_name   TEXT     NOT NULL,
    file_path   TEXT     NOT NULL,
    file_hash   TEXT,
    file_size   INTEGER,
    created_by  INTEGER,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    status      TEXT     DEFAULT 'Active',
    FOREIGN KEY (document_id) REFERENCES document_holder (id) ON DELETE CASCADE,
    FOREIGN KEY (created_by)  REFERENCES app_user (id)        ON DELETE SET NULL,
    UNIQUE (document_id, version_no)
);

-- ============================================================
-- TABLE: tbl_reader_log
-- Hardware / audit event log (RFID reader events + system ops)
-- ============================================================
CREATE TABLE IF NOT EXISTS tbl_reader_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    code         TEXT,
    log_datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    log_status   TEXT,
    log_message  TEXT
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_document_department   ON document_holder  (department_id);
CREATE INDEX IF NOT EXISTS idx_document_reference    ON document_holder  (reference_no);
CREATE INDEX IF NOT EXISTS idx_document_holder_dept  ON document_holder  (current_holder_department_id);
CREATE INDEX IF NOT EXISTS idx_version_document      ON document_version (document_id);
CREATE INDEX IF NOT EXISTS idx_movement_document     ON document_movement(document_id);
CREATE INDEX IF NOT EXISTS idx_reader_log_code       ON tbl_reader_log   (code, log_datetime);

-- ============================================================
-- TRIGGER: trg_update_current_version_after_insert
-- Keeps document_holder.current_version_id pointing at the
-- latest version whenever a new document_version row is added.
-- ============================================================
CREATE TRIGGER IF NOT EXISTS trg_update_current_version_after_insert
AFTER INSERT ON document_version
BEGIN
    UPDATE document_holder
    SET    current_version_id = NEW.id
    WHERE  id = NEW.document_id
      AND (
            current_version_id IS NULL
            OR NEW.version_no >= COALESCE(
                (SELECT version_no FROM document_version WHERE id = current_version_id),
                0
            )
          );
END;

-- ============================================================
-- TRIGGER: trg_update_holder_after_movement
-- Keeps document_holder denormalized columns in sync whenever
-- a document_movement row is inserted:
--   · current_holder_department_id → to_department_id
--   · current_holder_user_id       → moved_by
--   · last_movement_id             → NEW.id
-- ============================================================
CREATE TRIGGER IF NOT EXISTS trg_update_holder_after_movement
AFTER INSERT ON document_movement
BEGIN
    UPDATE document_holder
    SET    current_holder_department_id = NEW.to_department_id,
           current_holder_user_id       = NEW.moved_by,
           last_movement_id             = NEW.id
    WHERE  id = NEW.document_id;
END;

-- ============================================================
-- TRIGGER: trg_log_version_insert
-- Audit trail: writes to tbl_reader_log on every new version.
-- ============================================================
CREATE TRIGGER IF NOT EXISTS trg_log_version_insert
AFTER INSERT ON document_version
BEGIN
    INSERT INTO tbl_reader_log (code, log_status, log_message)
    VALUES (
        'DOC_VERSION_ADD',
        'SUCCESS',
        'Added version ' || NEW.version_no || ' for doc_id=' || NEW.document_id
    );
END;
