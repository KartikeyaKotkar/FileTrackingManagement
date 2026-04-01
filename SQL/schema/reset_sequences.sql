-- Reset all SERIAL sequences after manual data migration
SELECT setval('department_id_seq', (SELECT MAX(id) FROM department));
SELECT setval('role_id_seq', (SELECT MAX(id) FROM role));
SELECT setval('app_user_id_seq', (SELECT MAX(id) FROM app_user));
SELECT setval('document_holder_id_seq', (SELECT MAX(id) FROM document_holder));
SELECT setval('document_movement_id_seq', (SELECT MAX(id) FROM document_movement));
SELECT setval('document_version_id_seq', (SELECT MAX(id) FROM document_version));
SELECT setval('file_event_id_seq', (SELECT MAX(id) FROM file_event));
SELECT setval('transfer_request_id_seq', (SELECT MAX(id) FROM transfer_request));
SELECT setval('tbl_reader_log_id_seq', (SELECT MAX(id) FROM tbl_reader_log));
