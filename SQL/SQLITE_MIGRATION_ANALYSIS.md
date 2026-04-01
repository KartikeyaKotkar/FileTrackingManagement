# SQLite Migration Analysis

## Scope

This document analyzes the current database in this repository and explains the downsides of moving it from PostgreSQL to SQLite.

Reviewed files:

- `schema/01_create_tables_postgres.sql`
- `schema/02_seed_data.sql`
- `schema/reset_sequences.sql`
- `documents/*.sql`
- `movement/*.sql`
- `users/*.sql`
- `versions/*.sql`
- `logs/*.sql`

## Current Database Shape

The current schema is a small document-tracking system with these main entities:

- `department`
- `role`
- `app_user`
- `document_holder`
- `document_movement`
- `document_version`
- `tbl_reader_log`
- `file_event`
- `transfer_request`

Key behavior in the current design:

- `document_holder` stores current state for each document.
- `document_version` stores version history.
- `document_movement` stores transfer history.
- Triggers automatically keep `document_holder.current_version_id`, `document_holder.current_holder_department_id`, `document_holder.current_holder_user_id`, and `document_holder.last_movement_id` in sync.
- A trigger also writes audit-style log entries into `tbl_reader_log` after version inserts.
- SQL scripts rely on PostgreSQL features such as `SERIAL`, `setval(...)`, `plpgsql` trigger functions, `ALTER TABLE ... ADD CONSTRAINT`, and `%s`-style parameter placeholders in application queries.

## Main Downsides Of Moving To SQLite

### 1. Lower Write Concurrency

This is the biggest practical downside.

The current design performs several write-heavy operations that can chain together:

- creating documents
- adding versions
- moving documents
- writing logs
- trigger-driven updates to `document_holder`

SQLite allows many readers, but only one writer at a time per database file. In a multi-user office system, concurrent actions such as document movement, upload/version creation, and logging can block each other more often than they would in PostgreSQL.

Impact on this schema:

- adding a version writes to `document_version`, then trigger-updates `document_holder`, then trigger-inserts into `tbl_reader_log`
- moving a document writes to `document_movement`, then trigger-updates `document_holder`
- two staff members updating different documents can still compete for the same database write lock

If this application is expected to have multiple simultaneous users, SQLite will be less robust under contention.

### 2. Trigger Logic Must Be Rewritten

The current schema uses PostgreSQL trigger functions written in `plpgsql`:

- `trg_update_current_version_after_insert_pkg()`
- `trg_update_holder_after_movement_pkg()`
- `trg_log_version_insert_pkg()`

SQLite supports triggers, but it does not support PostgreSQL trigger functions or `plpgsql`.

That means:

- every trigger must be rewritten in SQLite trigger syntax
- `CREATE OR REPLACE FUNCTION` is not portable
- trigger debugging and maintenance become more manual

This is not just a syntax change. The current trigger model is central to keeping document state correct.

### 3. Some Schema DDL Does Not Port Cleanly

Several parts of the schema are PostgreSQL-specific:

- `SERIAL PRIMARY KEY`
- `BIGINT`
- `TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
- `ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY ...`
- sequence reset via `setval(...)`

SQLite differences:

- `SERIAL` does not exist
- sequence objects such as `department_id_seq` do not exist in the same way
- `ALTER TABLE` is much more limited
- adding foreign keys after table creation is not handled the way PostgreSQL does it

Important consequence for this schema:

`document_holder` is created first and later receives circular foreign keys to:

- `document_movement`
- `document_version`

That pattern is easy in PostgreSQL. In SQLite, circular references and late-added constraints usually require redesigning the table creation order or recreating tables during migration.

### 4. Foreign Keys Are Easier To Misconfigure

PostgreSQL enforces foreign keys by default once they are defined.

SQLite supports foreign keys, but enforcement must be enabled with:

```sql
PRAGMA foreign_keys = ON;
```

This has to be set on each database connection unless the application or driver guarantees it.

Risk for this project:

- if a connection is opened without foreign key enforcement, invalid `document_id`, `department_id`, or `role_id` references can be inserted
- that would undermine the integrity of movement history, current holder state, and version history

For this schema, foreign key enforcement is important because most tables are linked.

### 5. Weaker Type Enforcement

PostgreSQL has strong typing. SQLite uses dynamic type affinity.

This matters for fields such as:

- `file_size BIGINT`
- `created_at TIMESTAMP`
- `status TEXT CHECK (...)`
- `is_active INTEGER`
- `is_deleted INTEGER`

Downside:

- SQLite is more permissive about what gets inserted into a column
- application bugs are more likely to show up as bad data instead of immediate database errors

This is manageable, but it shifts more validation responsibility into the application.

### 6. Application SQL Must Change

The query files use `%s` placeholders, which are typical for PostgreSQL drivers such as `psycopg`.

SQLite drivers usually expect placeholders like:

- `?`
- `:name`

Examples affected:

- `documents/create_document.sql`
- `users/create_user.sql`
- `versions/create_version.sql`
- all lookup and update scripts

So even if the schema is migrated, the application-side SQL execution layer must also be updated.

Additional compatibility note:

- `RETURNING id` is used in multiple insert scripts

Modern SQLite supports `RETURNING`, but not all deployed SQLite versions do. If the runtime SQLite version is old, these scripts would need another rewrite.

### 7. Sequence Reset Logic Becomes Invalid

`schema/reset_sequences.sql` is PostgreSQL-only:

```sql
SELECT setval('department_id_seq', (SELECT MAX(id) FROM department));
```

SQLite has no direct equivalent sequence reset flow for this schema.

If migration/import scripts currently depend on explicit sequence repair after manual inserts, that operational pattern has to be redesigned.

### 8. Timestamp Semantics Become Simpler But Less Strict

The schema relies on `CURRENT_TIMESTAMP` in many places.

SQLite stores timestamps more loosely, often as text. That can introduce differences in:

- formatting
- timezone assumptions
- date comparisons
- driver-level parsing behavior

PostgreSQL gives more predictable timestamp behavior for long-term reporting and auditing.

This matters here because movement history, audit logs, version chronology, and user sorting all rely on timestamps.

### 9. Less Suitable For Networked Multi-User Deployment

PostgreSQL is a server database. SQLite is a file database.

That creates operational downsides if this system grows:

- weaker support for many concurrent users
- file locking sensitivity on shared/network drives
- fewer built-in administrative controls
- no server-side role model comparable to PostgreSQL
- harder separation between application and database responsibilities

For a single-user or light local deployment, SQLite can work well. For a shared office workflow with concurrent staff activity, PostgreSQL is the safer fit.

### 10. Future Schema Evolution Gets Harder

The current schema already uses:

- multiple foreign keys
- circular references
- triggers
- audit logging
- status constraints

SQLite can support a lot of this, but schema evolution is less flexible. Changes that are routine in PostgreSQL often require table recreation in SQLite.

That increases migration risk for future changes such as:

- adding new constraints
- restructuring foreign keys
- changing column definitions
- expanding audit behavior

## Areas That Would Need Rework During Migration

If a move to SQLite is attempted, these parts must be rewritten, not just copied:

- all `SERIAL` columns
- all trigger functions
- the circular foreign key setup on `document_holder`
- the `reset_sequences.sql` script
- all `%s` parameter placeholders
- any code relying on PostgreSQL-specific transaction or locking behavior

## Summary

For this specific database, the main downside of moving to SQLite is not raw feature loss in isolation. The real downside is that the current design depends on PostgreSQL-style integrity and write behavior:

- trigger-driven state synchronization
- relational integrity across many linked tables
- predictable concurrent writes
- PostgreSQL-specific DDL and maintenance scripts

SQLite can probably support a simplified version of this system, but it is a worse fit if the application is multi-user, write-active, or expected to evolve. The migration would also require non-trivial rewrites to both schema and application SQL, not just a database export/import.
