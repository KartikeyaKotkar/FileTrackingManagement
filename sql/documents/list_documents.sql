SELECT
  d.id,
  d.reference_no,
  d.title,
  d.status,
  d.created_at,
  own_dept.name AS owning_department,
  hold_dept.name AS current_holder_department,
  u.fullname AS current_holder_name,
  v.version_no AS current_version,
  m.moved_at AS last_movement_at,
  m.movement_type AS last_movement_type
FROM document_holder d
LEFT JOIN department own_dept ON d.department_id = own_dept.id
LEFT JOIN department hold_dept ON d.current_holder_department_id = hold_dept.id
LEFT JOIN app_user u ON d.current_holder_user_id = u.id
LEFT JOIN document_version v ON d.current_version_id = v.id
LEFT JOIN document_movement m ON d.last_movement_id = m.id
ORDER BY d.created_at DESC;
