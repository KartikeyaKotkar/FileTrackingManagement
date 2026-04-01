SELECT
    u.id,
    u.username,
    u.fullname,
    u.email,
    u.phone,
    u.role_id,
    r.role_name,
    u.is_active,
    u.created_at
FROM app_user u
LEFT JOIN role r ON u.role_id = r.id
WHERE u.id         = %s
  AND u.is_deleted = 0
LIMIT 1;
