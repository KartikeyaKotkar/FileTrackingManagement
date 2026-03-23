-- ============================================================
-- migrate.sql
-- Safe migration for existing township.db instances.
-- Run this INSTEAD of 01_create_tables.sql if you already
-- have data in the database.
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- STEP 1: Add new columns to document_holder
-- If a column already exists SQLite will error — safe to ignore.
-- ------------------------------------------------------------

ALTER TABLE document_holder ADD COLUMN current_holder_user_id       INTEGER REFERENCES app_user (id);
ALTER TABLE document_holder ADD COLUMN current_holder_department_id INTEGER REFERENCES department (id);
ALTER TABLE document_holder ADD COLUMN last_movement_id             INTEGER REFERENCES document_movement (id);

-- ------------------------------------------------------------
-- STEP 2: Create role table (new)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS role (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT    NOT NULL UNIQUE
);

INSERT OR IGNORE INTO role (id, role_name) VALUES (1, 'Admin'), (2, 'Manager'), (3, 'User');

-- ------------------------------------------------------------
-- STEP 3: Add auth columns to app_user
-- Matches the senior's tblUser schema.
-- ------------------------------------------------------------

ALTER TABLE app_user ADD COLUMN password    TEXT;
ALTER TABLE app_user ADD COLUMN email       TEXT;
ALTER TABLE app_user ADD COLUMN phone       TEXT;
ALTER TABLE app_user ADD COLUMN role_id     INTEGER REFERENCES role (id);
ALTER TABLE app_user ADD COLUMN is_active   INTEGER NOT NULL DEFAULT 1;
ALTER TABLE app_user ADD COLUMN is_deleted  INTEGER NOT NULL DEFAULT 0;
ALTER TABLE app_user ADD COLUMN created_by  INTEGER;
ALTER TABLE app_user ADD COLUMN updated_at  DATETIME;

-- ------------------------------------------------------------
-- STEP 4: Drop old triggers and recreate all cleanly
-- ------------------------------------------------------------

DROP TRIGGER IF EXISTS trg_update_current_version_after_insert;
DROP TRIGGER IF EXISTS trg_update_holder_after_movement;
DROP TRIGGER IF EXISTS trg_log_version_insert;

CREATE TRIGGER trg_update_current_version_after_insert
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

CREATE TRIGGER trg_update_holder_after_movement
AFTER INSERT ON document_movement
BEGIN
    UPDATE document_holder
    SET    current_holder_department_id = NEW.to_department_id,
           current_holder_user_id       = NEW.moved_by,
           last_movement_id             = NEW.id
    WHERE  id = NEW.document_id;
END;

CREATE TRIGGER trg_log_version_insert
AFTER INSERT ON document_version
BEGIN
    INSERT INTO tbl_reader_log (code, log_status, log_message)
    VALUES (
        'DOC_VERSION_ADD',
        'SUCCESS',
        'Added version ' || NEW.version_no || ' for doc_id=' || NEW.document_id
    );
END;

-- ------------------------------------------------------------
-- STEP 5: Add new indexes
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_document_holder_dept ON document_holder (current_holder_department_id);
CREATE INDEX IF NOT EXISTS idx_user_role            ON app_user         (role_id);

-- ------------------------------------------------------------
-- STEP 6: Backfill document_holder holder columns
-- ------------------------------------------------------------

UPDATE document_holder
SET
    last_movement_id             = (
        SELECT id FROM document_movement
        WHERE  document_id = document_holder.id
        ORDER  BY moved_at DESC LIMIT 1
    ),
    current_holder_department_id = (
        SELECT to_department_id FROM document_movement
        WHERE  document_id = document_holder.id
        ORDER  BY moved_at DESC LIMIT 1
    ),
    current_holder_user_id       = (
        SELECT moved_by FROM document_movement
        WHERE  document_id = document_holder.id
        ORDER  BY moved_at DESC LIMIT 1
    );

-- ------------------------------------------------------------
-- STEP 7: Update existing admin seed user with password
-- ------------------------------------------------------------

UPDATE app_user
SET    password = 'pbkdf2_sha256$100000$19+l//396ke6UJFFxaC0uA==$pr0+rF+g8W/RIMm9ipFqQIGzNNNpeR/+taOTCs3UZ6M=',
       role_id = 1,
       is_active = 1,
       is_deleted = 0
WHERE  username = 'admin';

-- ------------------------------------------------------------
-- Validation (uncomment to check manually):
-- SELECT name FROM sqlite_master WHERE type = 'trigger';
-- SELECT id, username, password, role_id, is_active FROM app_user;
-- SELECT * FROM role;
-- ------------------------------------------------------------
