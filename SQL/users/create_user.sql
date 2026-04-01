INSERT INTO app_user (username, fullname, password, email, phone, role_id, is_active, is_deleted, created_by)
VALUES (%s, %s, %s, %s, %s, %s, 1, 0, %s) RETURNING id;
