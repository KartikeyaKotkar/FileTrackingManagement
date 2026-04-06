INSERT INTO department (id, name) VALUES (1, 'Admin'), (2, 'IT'), (3, 'Finance'), (4, 'HR') ON CONFLICT (id) DO NOTHING;
INSERT INTO role (id, role_name) VALUES (1, 'Admin'), (2, 'Manager'), (3, 'User') ON CONFLICT (id) DO NOTHING;
INSERT INTO app_user (id, username, fullname, password, role_id, department_id, is_active, is_deleted)
VALUES (
    1,
    'admin',
    'Administrator',
    'pbkdf2_sha256$100000$YWRtaW5fc2VlZF9zYWx0IQ==$jETMkV3j8iSqTAzx4rDTAiVjxE8zmzWlKhYKmBfBwlc=',
    1,
    1,
    1,
    0
) ON CONFLICT (id) DO NOTHING;
