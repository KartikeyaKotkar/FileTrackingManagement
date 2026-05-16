-- Live migration: Fix existing database to match corrected schema
-- Run this against your existing file_tracking database

-- 1. Add missing to_user_id column to transfer_request (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'transfer_request' AND column_name = 'to_user_id'
    ) THEN
        ALTER TABLE transfer_request ADD COLUMN to_user_id INTEGER REFERENCES app_user (id);
    END IF;
END $$;

-- 2. Fix document_holder status CHECK constraint to allow 'Pending Transfer'
--    Drop the old constraint and add the new one
DO $$
BEGIN
    -- Find and drop the existing check constraint on status
    IF EXISTS (
        SELECT 1 FROM information_schema.check_constraints cc
        JOIN information_schema.constraint_column_usage ccu ON cc.constraint_name = ccu.constraint_name
        WHERE ccu.table_name = 'document_holder' AND ccu.column_name = 'status'
    ) THEN
        EXECUTE (
            SELECT 'ALTER TABLE document_holder DROP CONSTRAINT ' || cc.constraint_name
            FROM information_schema.check_constraints cc
            JOIN information_schema.constraint_column_usage ccu ON cc.constraint_name = ccu.constraint_name
            WHERE ccu.table_name = 'document_holder' AND ccu.column_name = 'status'
            LIMIT 1
        );
    END IF;
    
    -- Add the corrected constraint
    ALTER TABLE document_holder ADD CONSTRAINT document_holder_status_check
        CHECK (status IN ('Open', 'Active', 'Closed', 'Pending Transfer'));
END $$;

-- 3. Reset sequences to avoid duplicate key errors
SELECT setval(pg_get_serial_sequence('department', 'id'), COALESCE((SELECT MAX(id) FROM department), 1));
SELECT setval(pg_get_serial_sequence('role', 'id'), COALESCE((SELECT MAX(id) FROM role), 1));
SELECT setval(pg_get_serial_sequence('app_user', 'id'), COALESCE((SELECT MAX(id) FROM app_user), 1));
SELECT setval(pg_get_serial_sequence('document_holder', 'id'), COALESCE((SELECT MAX(id) FROM document_holder), 1));
SELECT setval(pg_get_serial_sequence('document_movement', 'id'), COALESCE((SELECT MAX(id) FROM document_movement), 1));
SELECT setval(pg_get_serial_sequence('document_version', 'id'), COALESCE((SELECT MAX(id) FROM document_version), 1));
SELECT setval(pg_get_serial_sequence('file_event', 'id'), COALESCE((SELECT MAX(id) FROM file_event), 1));
SELECT setval(pg_get_serial_sequence('transfer_request', 'id'), COALESCE((SELECT MAX(id) FROM transfer_request), 1));
SELECT setval(pg_get_serial_sequence('tbl_reader_log', 'id'), COALESCE((SELECT MAX(id) FROM tbl_reader_log), 1));
