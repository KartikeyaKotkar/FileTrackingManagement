-- Login: match username OR email + password
-- Only returns active, non-deleted users
SELECT
    u.id,
    u.username,
    u.fullname,
    u.password,
    u.email,
    u.phone,
    u.role_id,
    r.role_name,
    u.is_active,
    u.created_at
FROM app_user u
LEFT JOIN role r ON u.role_id = r.id
WHERE (u.username = %s OR u.email = %s)
  AND u.is_active  = 1
  AND u.is_deleted = 0
LIMIT 1;
