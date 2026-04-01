-- Postgres Schema Migration
-- ============================================================
-- EXTENSIONS
-- ============================================================
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- Not needed based on current schema but good for future.

-- ============================================================
-- TABLE: department
-- ============================================================
CREATE TABLE IF NOT EXISTS department (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    description TEXT,
    created_by  INTEGER
);

-- ============================================================
-- TABLE: role
-- ============================================================
CREATE TABLE IF NOT EXISTS role (
    id        SERIAL PRIMARY KEY,
    role_name TEXT NOT NULL UNIQUE
);

-- ============================================================
-- TABLE: app_user
-- ============================================================
CREATE TABLE IF NOT EXISTS app_user (
    id           SERIAL PRIMARY KEY,
    username     TEXT NOT NULL UNIQUE,
    fullname     TEXT,
    password     TEXT,
    email        TEXT,
    phone        TEXT,
    role_id      INTEGER REFERENCES role (id),
    department_id INTEGER REFERENCES department (id), -- Explicitly added department_id if needed, though not in the snippet above (wait, was it?)
    is_active    INTEGER NOT NULL DEFAULT 1,
    is_deleted   INTEGER NOT NULL DEFAULT 0,
    created_by   INTEGER,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP
);

-- ============================================================
-- TABLE: document_holder (Forward declaration-ish, FKs added later)
-- ============================================================
CREATE TABLE IF NOT EXISTS document_holder (
    id                           SERIAL PRIMARY KEY,
    reference_no                 TEXT NOT NULL UNIQUE,
    title                        TEXT NOT NULL,
    department_id                INTEGER NOT NULL DEFAULT 1 REFERENCES department (id) ON DELETE RESTRICT,
    current_version_id           INTEGER,
    current_holder_user_id       INTEGER REFERENCES app_user (id),
    current_holder_department_id INTEGER REFERENCES department (id),
    last_movement_id             INTEGER,
    status                       TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Open', 'Active', 'Closed')),
    created_by                   INTEGER REFERENCES app_user (id) ON DELETE SET NULL,
    created_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: document_movement
-- ============================================================
CREATE TABLE IF NOT EXISTS document_movement (
    id                 SERIAL PRIMARY KEY,
    document_id        INTEGER NOT NULL REFERENCES document_holder (id) ON DELETE CASCADE,
    from_department_id INTEGER REFERENCES department (id),
    to_department_id   INTEGER REFERENCES department (id),
    movement_type      TEXT DEFAULT 'Transfer',
    approved_by        INTEGER REFERENCES app_user (id),
    moved_by           INTEGER REFERENCES app_user (id),
    moved_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remarks            TEXT
);

-- ============================================================
-- TABLE: document_version
-- ============================================================
CREATE TABLE IF NOT EXISTS document_version (
    id          SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES document_holder (id) ON DELETE CASCADE,
    version_no  INTEGER NOT NULL,
    file_name   TEXT NOT NULL,
    file_path   TEXT NOT NULL,
    file_hash   TEXT,
    file_size   BIGINT,
    created_by  INTEGER REFERENCES app_user (id) ON DELETE SET NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status      TEXT DEFAULT 'Active',
    UNIQUE (document_id, version_no)
);

-- ============================================================
-- TABLE: tbl_reader_log
-- ============================================================
CREATE TABLE IF NOT EXISTS tbl_reader_log (
    id           SERIAL PRIMARY KEY,
    code         TEXT,
    log_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    log_status   TEXT,
    log_message  TEXT
);

-- ============================================================
-- ADD CIRCULAR FOREIGN KEYS
-- ============================================================
ALTER TABLE document_holder ADD CONSTRAINT fk_document_holder_last_movement_id FOREIGN KEY (last_movement_id) REFERENCES document_movement (id);
ALTER TABLE document_holder ADD CONSTRAINT fk_document_holder_current_version_id FOREIGN KEY (current_version_id) REFERENCES document_version (id);


-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_document_department   ON document_holder  (department_id);
CREATE INDEX IF NOT EXISTS idx_document_reference    ON document_holder  (reference_no);
CREATE INDEX IF NOT EXISTS idx_document_holder_dept  ON document_holder  (current_holder_department_id);
CREATE INDEX IF NOT EXISTS idx_version_document      ON document_version (document_id);
CREATE INDEX IF NOT EXISTS idx_movement_document     ON document_movement(document_id);
CREATE INDEX IF NOT EXISTS idx_reader_log_code       ON tbl_reader_log   (code, log_datetime);
CREATE INDEX IF NOT EXISTS idx_user_role             ON app_user         (role_id);

-- ============================================================
-- TABLE: file_event
-- ============================================================
CREATE TABLE IF NOT EXISTS file_event (
    id              SERIAL PRIMARY KEY,
    file_id         INTEGER REFERENCES document_holder (id),
    action          TEXT,
    performed_by    INTEGER REFERENCES app_user (id),
    from_department INTEGER REFERENCES department (id),
    to_department   INTEGER REFERENCES department (id),
    timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: transfer_request
-- ============================================================
CREATE TABLE IF NOT EXISTS transfer_request (
    id                  SERIAL PRIMARY KEY,
    file_id             INTEGER NOT NULL REFERENCES document_holder (id),
    from_department_id  INTEGER NOT NULL REFERENCES department (id),
    to_department_id    INTEGER NOT NULL REFERENCES department (id),
    requested_by        INTEGER NOT NULL REFERENCES app_user (id),
    status              TEXT DEFAULT 'pending',
    approved_by         INTEGER REFERENCES app_user (id),
    timestamp           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TRIGGERS
-- ============================================================

-- TRG: trg_update_current_version_after_insert
CREATE OR REPLACE FUNCTION trg_update_current_version_after_insert_pkg()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE document_holder
    SET    current_version_id = NEW.id
    WHERE  id = NEW.document_id
      AND (
            current_version_id IS NULL
            OR NEW.version_no >= COALESCE(
                (SELECT version_no FROM document_version WHERE id = (SELECT current_version_id FROM document_holder WHERE id = NEW.document_id)),
                0
            )
          );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_current_version_after_insert
AFTER INSERT ON document_version
FOR EACH ROW EXECUTE FUNCTION trg_update_current_version_after_insert_pkg();

-- TRG: trg_update_holder_after_movement
CREATE OR REPLACE FUNCTION trg_update_holder_after_movement_pkg()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE document_holder
    SET    current_holder_department_id = NEW.to_department_id,
           current_holder_user_id       = NEW.moved_by,
           last_movement_id             = NEW.id
    WHERE  id = NEW.document_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_holder_after_movement
AFTER INSERT ON document_movement
FOR EACH ROW EXECUTE FUNCTION trg_update_holder_after_movement_pkg();

-- TRG: trg_log_version_insert
CREATE OR REPLACE FUNCTION trg_log_version_insert_pkg()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO tbl_reader_log (code, log_status, log_message)
    VALUES (
        'DOC_VERSION_ADD',
        'SUCCESS',
        'Added version ' || NEW.version_no || ' for doc_id=' || NEW.document_id
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_log_version_insert
AFTER INSERT ON document_version
FOR EACH ROW EXECUTE FUNCTION trg_log_version_insert_pkg();
