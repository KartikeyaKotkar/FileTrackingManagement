SELECT d.*, v.version_no AS current_version_no, v.file_path AS current_file_path
FROM document_holder d
LEFT JOIN document_version v ON d.current_version_id = v.id
WHERE d.id = ?;
