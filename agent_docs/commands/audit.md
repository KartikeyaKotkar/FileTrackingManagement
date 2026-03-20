# Backend Audit Checklist

Used by the `/audit` agent. Check every item and report findings.

## 1. Schema vs Code Mismatches

- Compare columns in `sql/schema/restore.sql` against INSERT statements in `database.py`
- Check `DocumentCreate` schema in `schemas.py` — does it match what `create_document_with_version()` actually inserts?
- Check `VersionCreate` — does every field in the Pydantic model get passed through to `add_version()`?
- Check `MovementCreate` — does every field map correctly to `move_document()`?
- Verify `sql/documents/create_document.sql` is NOT used anywhere (it has a `status` column that `database.py` doesn't pass — potential dead file)

## 2. SQL File vs sql_loader Usage

- List all `.sql` files under `sql/`
- Check which ones are actually referenced in Python code via `sql.<category>.<stem>`
- Flag any `.sql` files that are never referenced (dead files)
- Flag any `sql.<category>.<stem>` references that don't have a corresponding `.sql` file

## 3. Router Completeness

- Every router should have GET (list), GET (single), POST at minimum
- `documents.py` — missing PATCH for status update (`update_document_status.sql` exists but is never called)
- Check if any router references a schema field that doesn't exist on the Pydantic model

## 4. Auth & Security

- `/auth/register` and `/auth/users` require `X-Admin-Key` header — verify `require_admin()` is called on both
- `/auth/login` should NOT require the admin key — verify it doesn't
- Check that `MASTER_KEY` is not committed with a weak or default value

## 5. Database Connection Safety

- All write operations (`INSERT`, `UPDATE`) should use explicit `BEGIN` / `COMMIT` / `ROLLBACK`
- `fetch_all` and `fetch_one` are read-only — verify they never execute writes
- Check `isolation_level=None` in `get_conn()` is intentional (autocommit mode, transactions managed manually)

## 6. Error Handling

- Every router endpoint should handle at minimum: not found (404), constraint errors (409), unexpected (500)
- Check which endpoints return raw exceptions vs proper HTTPException

## 7. Seed Data Consistency

- `sql/schema/02_seed_data.sql` uses old `app_user` schema (no `password`, `role_id` columns) — this is superseded by `restore.sql` and may cause confusion
- Verify `restore.sql` is the single source of truth for fresh setups

## 8. Trigger Correctness

- `trg_update_current_version_after_insert` — verify it won't downgrade `current_version_id` if an older version is inserted
- `trg_update_holder_after_movement` — verify it correctly sets `current_holder_user_id` to `moved_by`, not `approved_by`
- `trg_log_version_insert` — purely audit, verify it doesn't block on failure

## 9. Missing Features vs README

- README mentions `GET /auth/users` requires no auth — code says it does require `X-Admin-Key`. Flag this discrepancy.
- README shows `POST /documents/` body with `"description"` field — schemas.py has no `description` field. Flag.
- README shows `POST /movement/` body with `from_user`/`to_user` — actual schema uses `from_dept`/`to_dept` as integers. Flag.
