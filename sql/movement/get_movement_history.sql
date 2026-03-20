SELECT
  m.*,
  fd.name AS from_department_name,
  td.name AS to_department_name,
  approver.fullname AS approved_by_name,
  mover.fullname AS moved_by_name
FROM document_movement m
LEFT JOIN department fd ON m.from_department_id = fd.id
LEFT JOIN department td ON m.to_department_id = td.id
LEFT JOIN app_user approver ON m.approved_by = approver.id
LEFT JOIN app_user mover ON m.moved_by = mover.id
WHERE m.document_id = ?
ORDER BY m.moved_at DESC;
