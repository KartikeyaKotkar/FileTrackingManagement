SELECT v.* FROM document_holder d
JOIN document_version v ON d.current_version_id = v.id
WHERE d.id = ?;
