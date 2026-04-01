INSERT INTO document_movement (document_id, from_department_id, to_department_id, movement_type, approved_by, moved_by, remarks)
VALUES (%s, %s, %s, %s, %s, %s, %s);
