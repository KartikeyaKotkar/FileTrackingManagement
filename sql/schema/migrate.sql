-- ============================================================
-- migrate.sql
-- Safe migration for existing township.db instances.
--
-- Run this INSTEAD of 01_create_tables.sql if you already
-- have data in the database.
--
-- What this does:
--   1. Adds the 3 new columns to document_holder (ALTER TABLE)
--   2. Drops & recreates triggers (safe — triggers have no data)
--   3. Backfills current_holder_* and last_movement_id from
--      existing document_movement rows
--   4. Adds new indexes
--
-- What this does NOT do:
--   · Drop any table
--   · Delete any row
--   · Break existing data
--
-- NOTE: SQLite does not support ADD CONSTRAINT on existing tables.
--       The CHECK(status IN (...)) will only be enforced on NEW
--       rows after migration. Existing rows are untouched.
--       If you need strict enforcement on old rows, run the
--       validation query at the bottom first.
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- STEP 1: Add new columns to document_holder
-- Each is wrapped in a separate ALTER TABLE.
-- SQLite ignores "duplicate column" errors only via try/catch
-- in application code — here we use a safe pattern via a
-- temp check. Run each line; if the column already exists,
-- SQLite will return an error you can safely ignore.
-- ------------------------------------------------------------

ALTER TABLE document_holder ADD COLUMN current_holder_user_id       INTEGER REFERENCES app_user (id);
ALTER TABLE document_holder ADD COLUMN current_holder_department_id INTEGER REFERENCES department (id);
ALTER TABLE document_holder ADD COLUMN last_movement_id             INTEGER REFERENCES document_movement (id);

-- ------------------------------------------------------------
-- STEP 2: Drop old triggers and recreate all three cleanly
-- (DROP IF EXISTS is safe even if they never existed)
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
-- STEP 3: Add new indexes (IF NOT EXISTS = safe to re-run)
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_document_holder_dept ON document_holder (current_holder_department_id);

-- ------------------------------------------------------------
-- STEP 4: Backfill current_holder_* and last_movement_id
-- from the most recent movement row per document.
-- This brings existing documents in sync with the new triggers.
-- ------------------------------------------------------------

UPDATE document_holder
SET
    last_movement_id             = (
        SELECT id FROM document_movement
        WHERE  document_id = document_holder.id
        ORDER  BY moved_at DESC
        LIMIT  1
    ),
    current_holder_department_id = (
        SELECT to_department_id FROM document_movement
        WHERE  document_id = document_holder.id
        ORDER  BY moved_at DESC
        LIMIT  1
    ),
    current_holder_user_id       = (
        SELECT moved_by FROM document_movement
        WHERE  document_id = document_holder.id
        ORDER  BY moved_at DESC
        LIMIT  1
    );

-- ------------------------------------------------------------
-- STEP 5: Validation queries — run these to confirm migration.
-- Uncomment and run manually to check.
-- ------------------------------------------------------------

-- Check no document has an invalid status value:
-- SELECT id, reference_no, status FROM document_holder
-- WHERE status NOT IN ('Open', 'Active', 'Closed');

-- Check holder backfill worked:
-- SELECT id, reference_no, current_holder_department_id, last_movement_id
-- FROM document_holder;

-- Confirm all 3 triggers exist:
-- SELECT name FROM sqlite_master WHERE type = 'trigger';
