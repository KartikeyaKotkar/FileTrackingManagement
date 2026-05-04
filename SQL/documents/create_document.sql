INSERT INTO document_holder (reference_no, tag_number, title, department_id, created_by)
VALUES (%s, %s, %s, %s, %s) RETURNING id;
