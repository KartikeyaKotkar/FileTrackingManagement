#!/usr/bin/env python3
"""
Seed synthetic defence-style demo data for FileTrackingManagement.

This data is fictional and unclassified. It is not official DRDO data.
The script is idempotent: existing usernames, departments, references,
versions, movements, transfers, and tag reads are skipped.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.security import hash_password  # noqa: E402


DEFAULT_DATABASE_URL = "postgresql://filetracking_user:filetracking_password@localhost:5432/file_tracking"
DEFAULT_PASSWORD = "Demo@12345"


DEPARTMENTS = [
    ("Advanced Systems Registry", "Controlled registry for prototype system files."),
    ("Guidance Control Archive", "File control for guidance and control work packages."),
    ("Materials Evaluation Cell", "Document custody for materials test records."),
    ("Secure Trials Office", "Movement desk for range trial documentation."),
    ("Stores Movement Control", "Inventory-linked document tracking office."),
    ("Telemetry Analysis Group", "Archive for telemetry review and readout records."),
]

USERS = [
    ("registry.officer", "Registry Officer", "registry.officer@example.invalid", "9000000101", "Advanced Systems Registry"),
    ("guidance.clerk", "Guidance Records Clerk", "guidance.clerk@example.invalid", "9000000102", "Guidance Control Archive"),
    ("materials.custodian", "Materials Custodian", "materials.custodian@example.invalid", "9000000103", "Materials Evaluation Cell"),
    ("trials.coordinator", "Trials Coordinator", "trials.coordinator@example.invalid", "9000000104", "Secure Trials Office"),
    ("stores.controller", "Stores Controller", "stores.controller@example.invalid", "9000000105", "Stores Movement Control"),
    ("telemetry.analyst", "Telemetry Analyst", "telemetry.analyst@example.invalid", "9000000106", "Telemetry Analysis Group"),
]

DOCUMENTS = [
    ("DRDO-DEMO-2026-0001", "RFID-DRDO-DMO-0001", "Prototype Assembly Receipt Register", "Advanced Systems Registry", "registry.officer", "Active"),
    ("DRDO-DEMO-2026-0002", "RFID-DRDO-DMO-0002", "Guidance Bench Calibration Log", "Guidance Control Archive", "guidance.clerk", "Active"),
    ("DRDO-DEMO-2026-0003", "RFID-DRDO-DMO-0003", "Composite Panel Inspection Docket", "Materials Evaluation Cell", "materials.custodian", "Active"),
    ("DRDO-DEMO-2026-0004", "RFID-DRDO-DMO-0004", "Environmental Chamber Test Schedule", "Materials Evaluation Cell", "materials.custodian", "Active"),
    ("DRDO-DEMO-2026-0005", "RFID-DRDO-DMO-0005", "Range Trial Movement Note", "Secure Trials Office", "trials.coordinator", "Active"),
    ("DRDO-DEMO-2026-0006", "RFID-DRDO-DMO-0006", "Telemetry Readout Review Pack", "Telemetry Analysis Group", "telemetry.analyst", "Active"),
    ("DRDO-DEMO-2026-0007", "RFID-DRDO-DMO-0007", "Stores Gate Pass Control File", "Stores Movement Control", "stores.controller", "Active"),
    ("DRDO-DEMO-2026-0008", "RFID-DRDO-DMO-0008", "Subsystem Integration Checklist", "Advanced Systems Registry", "registry.officer", "Active"),
    ("DRDO-DEMO-2026-0009", "RFID-DRDO-DMO-0009", "Quality Observation Closure Sheet", "Guidance Control Archive", "guidance.clerk", "Closed"),
    ("DRDO-DEMO-2026-0010", "RFID-DRDO-DMO-0010", "Secure Dispatch Acknowledgement", "Stores Movement Control", "stores.controller", "Active"),
    ("DRDO-DEMO-2026-0011", "RFID-DRDO-DMO-0011", "Trial Instrumentation Handover", "Secure Trials Office", "trials.coordinator", "Active"),
    ("DRDO-DEMO-2026-0012", "RFID-DRDO-DMO-0012", "Telemetry Storage Verification Note", "Telemetry Analysis Group", "telemetry.analyst", "Active"),
]

VERSIONS = [
    ("DRDO-DEMO-2026-0001", 1, "prototype-assembly-receipt-v1.pdf", "/demo/defence/prototype-assembly-receipt-v1.pdf", "demo-hash-0001-v1", 248832),
    ("DRDO-DEMO-2026-0002", 1, "guidance-bench-calibration-v1.pdf", "/demo/defence/guidance-bench-calibration-v1.pdf", "demo-hash-0002-v1", 196608),
    ("DRDO-DEMO-2026-0003", 1, "composite-panel-inspection-v1.pdf", "/demo/defence/composite-panel-inspection-v1.pdf", "demo-hash-0003-v1", 221184),
    ("DRDO-DEMO-2026-0003", 2, "composite-panel-inspection-v2.pdf", "/demo/defence/composite-panel-inspection-v2.pdf", "demo-hash-0003-v2", 229376),
    ("DRDO-DEMO-2026-0004", 1, "environmental-chamber-schedule-v1.pdf", "/demo/defence/environmental-chamber-schedule-v1.pdf", "demo-hash-0004-v1", 180224),
    ("DRDO-DEMO-2026-0005", 1, "range-trial-movement-note-v1.pdf", "/demo/defence/range-trial-movement-note-v1.pdf", "demo-hash-0005-v1", 172032),
    ("DRDO-DEMO-2026-0006", 1, "telemetry-readout-review-v1.pdf", "/demo/defence/telemetry-readout-review-v1.pdf", "demo-hash-0006-v1", 286720),
    ("DRDO-DEMO-2026-0008", 1, "subsystem-integration-checklist-v1.pdf", "/demo/defence/subsystem-integration-checklist-v1.pdf", "demo-hash-0008-v1", 139264),
]

MOVEMENTS = [
    ("DRDO-DEMO-2026-0002", "Guidance Control Archive", "Advanced Systems Registry", "registry.officer", "Demo transfer for integration review"),
    ("DRDO-DEMO-2026-0005", "Secure Trials Office", "Telemetry Analysis Group", "telemetry.analyst", "Demo handover after trial readout"),
    ("DRDO-DEMO-2026-0010", "Stores Movement Control", "Secure Trials Office", "trials.coordinator", "Demo dispatch to trials desk"),
]

TRANSFERS = [
    ("DRDO-DEMO-2026-0004", "Materials Evaluation Cell", "Secure Trials Office", "materials.custodian", "trials.coordinator", "pending"),
    ("DRDO-DEMO-2026-0011", "Secure Trials Office", "Telemetry Analysis Group", "trials.coordinator", "telemetry.analyst", "pending"),
]

TAG_READS = [
    ("300833B2DDD9014D00000001", "Demo Gate Reader Alpha", 1, "2026-05-30T09:05:00+05:30", -43, "Main Registry Gate"),
    ("300833B2DDD9014D00000002", "Demo Gate Reader Alpha", 2, "2026-05-30T09:07:00+05:30", -48, "Main Registry Gate"),
    ("300833B2DDD9014D00000003", "Demo Lab Reader Bravo", 1, "2026-05-30T10:12:00+05:30", -51, "Materials Lab Entry"),
    ("300833B2DDD9014D00000004", "Demo Trial Bay Reader", 1, "2026-05-30T11:20:00+05:30", -46, "Secure Trials Bay"),
    ("300833B2DDD9014D00000005", "Demo Stores Reader", 3, "2026-05-30T12:35:00+05:30", -55, "Stores Dispatch Desk"),
    ("300833B2DDD9014D00000006", "Demo Telemetry Reader", 1, "2026-05-30T14:10:00+05:30", -49, "Telemetry Review Room"),
    ("300833B2DDD9014D00000007", "Demo Gate Reader Alpha", 1, "2026-05-31T09:15:00+05:30", -44, "Main Registry Gate"),
    ("300833B2DDD9014D00000008", "Demo Secure Archive Reader", 2, "2026-05-31T15:45:00+05:30", -52, "Secure Archive"),
]


@dataclass
class SeedState:
    departments: dict[str, int]
    users: dict[str, int]
    documents: dict[str, int]
    inserted: dict[str, int]
    skipped: dict[str, int]

    def add(self, bucket: str, inserted: bool) -> None:
        target = self.inserted if inserted else self.skipped
        target[bucket] = target.get(bucket, 0) + 1


def one(cur, query: str, params: tuple = ()) -> tuple | None:
    cur.execute(query, params)
    return cur.fetchone()


def scalar(cur, query: str, params: tuple = ()) -> int:
    row = one(cur, query, params)
    if row is None:
        raise RuntimeError(f"Expected row for query: {query}")
    return row[0]


def get_admin_id(cur) -> int:
    row = one(
        cur,
        """
        SELECT id
        FROM app_user
        WHERE username = %s
          AND role_id = (SELECT id FROM role WHERE role_name = %s)
          AND is_deleted = 0
        """,
        ("admin", "Admin"),
    )
    if row is None:
        raise RuntimeError("Admin user not found. Seed base schema first and do not delete admin.")
    return row[0]


def get_or_create_role(cur, role_name: str, state: SeedState) -> int:
    row = one(cur, "SELECT id FROM role WHERE role_name = %s", (role_name,))
    if row:
        state.add("roles", False)
        return row[0]
    role_id = scalar(cur, "INSERT INTO role (role_name) VALUES (%s) RETURNING id", (role_name,))
    state.add("roles", True)
    return role_id


def get_or_create_department(cur, name: str, description: str, admin_id: int, state: SeedState) -> int:
    row = one(cur, "SELECT id FROM department WHERE name = %s", (name,))
    if row:
        state.add("departments", False)
        return row[0]
    dept_id = scalar(
        cur,
        "INSERT INTO department (name, description, created_by) VALUES (%s, %s, %s) RETURNING id",
        (name, description, admin_id),
    )
    state.add("departments", True)
    return dept_id


def get_or_create_user(cur, user: tuple[str, str, str, str, str], role_id: int, password: str, admin_id: int, state: SeedState) -> int:
    username, fullname, email, phone, dept_name = user
    row = one(cur, "SELECT id FROM app_user WHERE username = %s", (username,))
    if row:
        state.add("users", False)
        return row[0]
    user_id = scalar(
        cur,
        """
        INSERT INTO app_user
            (username, fullname, password, email, phone, role_id, department_id, is_active, is_deleted, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 1, 0, %s)
        RETURNING id
        """,
        (username, fullname, hash_password(password), email, phone, role_id, state.departments[dept_name], admin_id),
    )
    state.add("users", True)
    return user_id


def get_or_create_document(cur, doc: tuple[str, str, str, str, str, str], state: SeedState) -> int:
    reference_no, tag_number, title, dept_name, username, status = doc
    row = one(cur, "SELECT id FROM document_holder WHERE reference_no = %s", (reference_no,))
    if row:
        state.add("documents", False)
        return row[0]
    dept_id = state.departments[dept_name]
    user_id = state.users[username]
    doc_id = scalar(
        cur,
        """
        INSERT INTO document_holder
            (reference_no, tag_number, title, department_id, current_holder_user_id,
             current_holder_department_id, status, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (reference_no, tag_number, title, dept_id, user_id, dept_id, status, user_id),
    )
    state.add("documents", True)
    insert_file_event(cur, doc_id, "created", user_id, None, dept_id, state)
    return doc_id


def insert_version(cur, version: tuple[str, int, str, str, str, int], state: SeedState) -> None:
    reference_no, version_no, file_name, file_path, file_hash, file_size = version
    doc_id = state.documents[reference_no]
    row = one(cur, "SELECT id FROM document_version WHERE document_id = %s AND version_no = %s", (doc_id, version_no))
    if row:
        state.add("versions", False)
        return
    created_by = scalar(cur, "SELECT created_by FROM document_holder WHERE id = %s", (doc_id,))
    scalar(
        cur,
        """
        INSERT INTO document_version
            (document_id, version_no, file_name, file_path, file_hash, file_size, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (doc_id, version_no, file_name, file_path, file_hash, file_size, created_by),
    )
    state.add("versions", True)
    insert_file_event(cur, doc_id, "updated", created_by, None, None, state)


def insert_file_event(cur, file_id: int, action: str, performed_by: int, from_dept: int | None, to_dept: int | None, state: SeedState) -> None:
    row = one(
        cur,
        """
        SELECT id FROM file_event
        WHERE file_id = %s
          AND action = %s
          AND performed_by = %s
          AND from_department IS NOT DISTINCT FROM %s
          AND to_department IS NOT DISTINCT FROM %s
        LIMIT 1
        """,
        (file_id, action, performed_by, from_dept, to_dept),
    )
    if row:
        state.add("file_events", False)
        return
    scalar(
        cur,
        """
        INSERT INTO file_event (file_id, action, performed_by, from_department, to_department)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (file_id, action, performed_by, from_dept, to_dept),
    )
    state.add("file_events", True)


def insert_movement(cur, movement: tuple[str, str, str, str, str], state: SeedState) -> None:
    reference_no, from_dept_name, to_dept_name, moved_by_username, remarks = movement
    doc_id = state.documents[reference_no]
    from_dept = state.departments[from_dept_name]
    to_dept = state.departments[to_dept_name]
    moved_by = state.users[moved_by_username]
    row = one(
        cur,
        """
        SELECT id FROM document_movement
        WHERE document_id = %s AND from_department_id = %s AND to_department_id = %s AND remarks = %s
        LIMIT 1
        """,
        (doc_id, from_dept, to_dept, remarks),
    )
    if row:
        state.add("movements", False)
        return
    scalar(
        cur,
        """
        INSERT INTO document_movement
            (document_id, from_department_id, to_department_id, movement_type, approved_by, moved_by, remarks)
        VALUES (%s, %s, %s, 'Transfer', %s, %s, %s)
        RETURNING id
        """,
        (doc_id, from_dept, to_dept, moved_by, moved_by, remarks),
    )
    state.add("movements", True)
    insert_file_event(cur, doc_id, "moved", moved_by, from_dept, to_dept, state)


def insert_transfer(cur, transfer: tuple[str, str, str, str, str, str], state: SeedState) -> None:
    reference_no, from_dept_name, to_dept_name, requested_by_username, to_user_username, status = transfer
    doc_id = state.documents[reference_no]
    from_dept = state.departments[from_dept_name]
    to_dept = state.departments[to_dept_name]
    requested_by = state.users[requested_by_username]
    to_user = state.users[to_user_username]
    row = one(
        cur,
        """
        SELECT id FROM transfer_request
        WHERE file_id = %s AND from_department_id = %s AND to_department_id = %s
          AND requested_by = %s AND to_user_id = %s AND status = %s
        LIMIT 1
        """,
        (doc_id, from_dept, to_dept, requested_by, to_user, status),
    )
    if row:
        state.add("transfers", False)
        return
    scalar(
        cur,
        """
        INSERT INTO transfer_request
            (file_id, from_department_id, to_department_id, requested_by, to_user_id, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (doc_id, from_dept, to_dept, requested_by, to_user, status),
    )
    state.add("transfers", True)


def insert_tag_read(cur, tag_read: tuple[str, str, int, str, int, str], state: SeedState) -> None:
    epc, reader_name, antenna, timestamp, rssi, location = tag_read
    row = one(
        cur,
        """
        SELECT id FROM tag_reads
        WHERE epc = %s AND reader_name = %s AND antenna = %s AND timestamp = %s::timestamptz
        LIMIT 1
        """,
        (epc, reader_name, antenna, timestamp),
    )
    if row:
        state.add("tag_reads", False)
        return
    scalar(
        cur,
        """
        INSERT INTO tag_reads (epc, reader_name, antenna, timestamp, rssi, location)
        VALUES (%s, %s, %s, %s::timestamptz, %s, %s)
        RETURNING id
        """,
        (epc, reader_name, antenna, timestamp, rssi, location),
    )
    state.add("tag_reads", True)


def repair_sequences(cur) -> None:
    tables = [
        "department",
        "role",
        "app_user",
        "document_holder",
        "document_movement",
        "document_version",
        "file_event",
        "transfer_request",
        "tag_reads",
        "tbl_reader_log",
    ]
    for table in tables:
        cur.execute(
            "SELECT setval(pg_get_serial_sequence(%s, 'id'), GREATEST((SELECT COALESCE(MAX(id), 1) FROM " + table + "), 1))",
            (table,),
        )


def clean_non_admin_data(cur, state: SeedState) -> None:
    admin_id = get_admin_id(cur)
    cur.execute(
        """
        UPDATE document_holder
        SET current_version_id = NULL,
            last_movement_id = NULL,
            current_holder_user_id = NULL,
            current_holder_department_id = NULL
        """
    )
    state.inserted["cleared_document_links"] = cur.rowcount

    deletes = [
        ("transfer_request", "DELETE FROM transfer_request"),
        ("file_event", "DELETE FROM file_event"),
        ("document_movement", "DELETE FROM document_movement"),
        ("document_version", "DELETE FROM document_version"),
        ("document_holder", "DELETE FROM document_holder"),
        ("tag_reads", "DELETE FROM tag_reads"),
        ("demo_users", "DELETE FROM app_user WHERE id <> %s"),
        ("demo_departments", "DELETE FROM department WHERE name <> %s"),
    ]

    for bucket, query in deletes:
        if bucket == "demo_users":
            cur.execute(query, (admin_id,))
        elif bucket == "demo_departments":
            cur.execute(query, ("Admin",))
        else:
            cur.execute(query)
        state.inserted[f"deleted_{bucket}"] = cur.rowcount


def reset_admin_password(cur, password: str) -> None:
    cur.execute(
        """
        UPDATE app_user
        SET password = %s,
            is_active = 1,
            is_deleted = 0
        WHERE username = %s
        """,
        (hash_password(password), "admin"),
    )
    if cur.rowcount != 1:
        raise RuntimeError("Expected exactly one admin user to reset.")


def print_plan() -> None:
    print("Plan only. No database writes.")
    print(f"Departments: {len(DEPARTMENTS)}")
    print(f"Users: {len(USERS)}")
    print(f"Documents: {len(DOCUMENTS)}")
    print(f"Versions: {len(VERSIONS)}")
    print(f"Movements: {len(MOVEMENTS)}")
    print(f"Pending transfers: {len(TRANSFERS)}")
    print(f"Tag reads: {len(TAG_READS)}")


def seed(database_url: str, password: str, admin_password: str, apply: bool, clean: bool, reset_admin: bool) -> SeedState:
    state = SeedState(departments={}, users={}, documents={}, inserted={}, skipped={})
    if not apply:
        print_plan()
        return state

    try:
        import psycopg2
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "psycopg2 is required for --apply. Run inside the backend container or install backend requirements."
        ) from exc

    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            if clean:
                clean_non_admin_data(cur, state)

            if reset_admin:
                reset_admin_password(cur, admin_password)

            admin_id = get_admin_id(cur)
            user_role_id = get_or_create_role(cur, "User", state)

            for name, description in DEPARTMENTS:
                state.departments[name] = get_or_create_department(cur, name, description, admin_id, state)

            for user in USERS:
                state.users[user[0]] = get_or_create_user(cur, user, user_role_id, password, admin_id, state)

            for doc in DOCUMENTS:
                state.documents[doc[0]] = get_or_create_document(cur, doc, state)

            for version in VERSIONS:
                insert_version(cur, version, state)

            for movement in MOVEMENTS:
                insert_movement(cur, movement, state)

            for transfer in TRANSFERS:
                insert_transfer(cur, transfer, state)

            for tag_read in TAG_READS:
                insert_tag_read(cur, tag_read, state)

            repair_sequences(cur)

    return state


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed fictional defence demo data.")
    parser.add_argument("--apply", action="store_true", help="Write demo data. Without this flag, only prints plan.")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL))
    parser.add_argument("--password", default=os.getenv("DEMO_USER_PASSWORD", DEFAULT_PASSWORD), help="Password for newly-created demo users.")
    parser.add_argument("--admin-password", default=os.getenv("ADMIN_PASSWORD", "admin"), help="Password to set for admin when --reset-admin-password is used.")
    parser.add_argument("--clean", action="store_true", help="Delete all non-admin application data before seeding.")
    parser.add_argument("--reset-admin-password", action="store_true", help="Reset admin password and keep admin active.")
    args = parser.parse_args()

    state = seed(args.database_url, args.password, args.admin_password, args.apply, args.clean, args.reset_admin_password)
    if args.apply:
        print("Demo seed complete.")
        print(f"Inserted: {state.inserted}")
        print(f"Skipped: {state.skipped}")
        if args.reset_admin_password:
            print(f"Admin password: {args.admin_password}")
        print(f"New demo user password: {args.password}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
