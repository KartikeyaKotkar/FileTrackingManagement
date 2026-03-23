INSERT OR IGNORE INTO department (id, name) VALUES (1, 'Admin'), (2, 'IT'), (3, 'Finance'), (4, 'HR');
INSERT OR IGNORE INTO role (id, role_name) VALUES (1, 'Admin'), (2, 'Manager'), (3, 'User');
INSERT OR IGNORE INTO app_user (id, username, fullname, password, role_id, is_active, is_deleted)
VALUES (
    1,
    'admin',
    'Administrator',
    'pbkdf2_sha256$100000$19+l//396ke6UJFFxaC0uA==$pr0+rF+g8W/RIMm9ipFqQIGzNNNpeR/+taOTCs3UZ6M=',
    1,
    1,
    0
);
