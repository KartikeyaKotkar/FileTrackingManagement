-- Reset all SERIAL sequences after manual data migration
SELECT setval('department_id_seq', COALESCE((SELECT MAX(id) FROM department), 1));
SELECT setval('role_id_seq', COALESCE((SELECT MAX(id) FROM role), 1));
SELECT setval('app_user_id_seq', COALESCE((SELECT MAX(id) FROM app_user), 1));
SELECT setval('document_holder_id_seq', COALESCE((SELECT MAX(id) FROM document_holder), 1));
SELECT setval('document_movement_id_seq', COALESCE((SELECT MAX(id) FROM document_movement), 1));
SELECT setval('document_version_id_seq', COALESCE((SELECT MAX(id) FROM document_version), 1));
SELECT setval('file_event_id_seq', COALESCE((SELECT MAX(id) FROM file_event), 1));
SELECT setval('transfer_request_id_seq', COALESCE((SELECT MAX(id) FROM transfer_request), 1));
SELECT setval('tbl_reader_log_id_seq', COALESCE((SELECT MAX(id) FROM tbl_reader_log), 1));
