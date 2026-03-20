SELECT
  v.*,
  u.fullname AS created_by_name
FROM document_version v
LEFT JOIN app_user u ON v.created_by = u.id
WHERE v.document_id = ?
ORDER BY v.version_no DESC;
