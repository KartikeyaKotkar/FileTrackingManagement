# Database Schema Reference

## Tables (in declaration order — matters for FK resolution)

1. `department` — id, name (UNIQUE)
2. `role` — id, role_name (UNIQUE)
3. `app_user` — id, username, fullname, password, email, phone, role_id, is_active, is_deleted, created_by, created_at, updated_at
4. `document_movement` — declared BEFORE document_holder (last_movement_id FK)
5. `document_holder` — id, reference_no, title, department_id, current_version_id, current_holder_user_id, current_holder_department_id, last_movement_id, status, created_by, created_at
6. `document_version` — id, document_id, version_no, file_name, file_path, file_hash, file_size, created_by, created_at, status
7. `tbl_reader_log` — id, code, log_datetime, log_status, log_message

## Auto-managed Columns (via triggers — never set manually)

| Column | Table | Trigger |
|--------|-------|---------|
| `current_version_id` | `document_holder` | `trg_update_current_version_after_insert` |
| `current_holder_department_id` | `document_holder` | `trg_update_holder_after_movement` |
| `current_holder_user_id` | `document_holder` | `trg_update_holder_after_movement` |
| `last_movement_id` | `document_holder` | `trg_update_holder_after_movement` |

## Seed Data (from restore.sql)

Departments: Admin(1), IT(2), Finance(3), HR(4)
Roles: Admin(1), Manager(2), User(3)
Default user: admin / Admin@123 / role_id=1

## Status Constraint

`document_holder.status` CHECK: `'Open' | 'Active' | 'Closed'`
