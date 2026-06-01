import asyncio
import importlib.util
import sys
import types
from datetime import timezone
from pathlib import Path

from fastapi import FastAPI
from app.models.schemas import TagReadCreate


def test_tag_read_schema_accepts_reader_name_alias_and_location():
    payload = {
        "epc": "  EPC-123  ",
        "readerName": "  Reader A  ",
        "antenna": 2,
        "timestamp": "2026-05-21T10:30:00+05:30",
        "rssi": -45,
        "location": "Shelf A-01 ",
    }

    data = TagReadCreate.model_validate(payload)

    assert data.epc == "EPC-123"
    assert data.reader_name == "Reader A"
    assert data.location == "Shelf A-01 "
    assert data.timestamp.tzinfo == timezone.utc


def test_tag_read_schema_coerces_string_antenna_and_naive_timestamp_to_utc():
    payload = {
        "epc": "EPC-123",
        "readerName": "Reader A",
        "antenna": "1",
        "timestamp": "2026-05-21T00:00:00",
        "rssi": -45,
        "location": "Main Gate",
    }

    data = TagReadCreate.model_validate(payload)

    assert data.antenna == 1
    assert data.timestamp.isoformat() == "2026-05-21T00:00:00+00:00"


def test_tag_read_schema_still_accepts_legacy_reader_name_field():
    payload = {
        "epc": "EPC-123",
        "reader_name": "Reader A",
        "antenna": 2,
        "timestamp": "2026-05-21T10:30:00+05:30",
        "rssi": -45,
        "location": "Dock 3",
    }

    data = TagReadCreate.model_validate(payload)

    assert data.reader_name == "Reader A"
    assert data.location == "Dock 3"


def test_tag_read_schema_accepts_hardware_pascal_case_payload_with_location():
    payload = {
        "EPC": "EPC-123",
        "ReaderName": "Reader A",
        "Antenna": 2,
        "Timestamp": "2026-05-21T10:30:00+05:30",
        "RSSI": -45,
        "Location": "Main Gate",
    }

    data = TagReadCreate.model_validate(payload)

    assert data.epc == "EPC-123"
    assert data.reader_name == "Reader A"
    assert data.antenna == 2
    assert data.rssi == -45
    assert data.location == "Main Gate"


def test_tag_read_schema_requires_location():
    payload = {
        "EPC": "EPC-123",
        "ReaderName": "Reader A",
        "Antenna": 2,
        "Timestamp": "2026-05-21T10:30:00+05:30",
        "RSSI": -45,
    }

    try:
        TagReadCreate.model_validate(payload)
    except Exception as exc:
        assert "location" in str(exc).lower()
    else:
        raise AssertionError("Expected validation error for missing location")


def test_create_tag_read_endpoint_passes_location_through(monkeypatch):
    captured = {}

    def fake_create_tag_read(epc, reader_name, antenna, timestamp, rssi, location):
        captured.update(
            {
                "epc": epc,
                "reader_name": reader_name,
                "antenna": antenna,
                "timestamp": timestamp,
                "rssi": rssi,
                "location": location,
            }
        )
        return {"id": 1, **captured}

    fake_database = types.ModuleType("app.database")
    fake_database.create_tag_read = fake_create_tag_read
    fake_database.get_tag_reads = lambda: []
    monkeypatch.setitem(sys.modules, "app.database", fake_database)

    module_path = Path(__file__).resolve().parents[1] / "app" / "routers" / "tag_reads.py"
    spec = importlib.util.spec_from_file_location("tag_reads_under_test", module_path)
    tag_reads = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(tag_reads)

    payload = TagReadCreate.model_validate(
        {
            "epc": "EPC-123",
            "readerName": "Reader A",
            "antenna": 2,
            "timestamp": "2026-05-21T10:30:00+05:30",
            "rssi": -45,
            "location": "Gate-7",
        }
    )
    response = asyncio.run(tag_reads.create_tag_read_endpoint(payload))

    assert captured["location"] == "Gate-7"
    assert response["tag_read"]["location"] == "Gate-7"


def test_create_tag_read_endpoint_ignores_duplicate(monkeypatch):
    fake_database = types.ModuleType("app.database")
    fake_database.create_tag_read = lambda *args, **kwargs: {"duplicate": True}
    fake_database.get_tag_reads = lambda: []
    monkeypatch.setitem(sys.modules, "app.database", fake_database)

    module_path = Path(__file__).resolve().parents[1] / "app" / "routers" / "tag_reads.py"
    spec = importlib.util.spec_from_file_location("tag_reads_duplicate_under_test", module_path)
    tag_reads = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(tag_reads)

    payload = TagReadCreate.model_validate(
        {
            "epc": "EPC-123",
            "readerName": "Reader A",
            "antenna": 2,
            "timestamp": "2026-05-21T10:30:00+05:30",
            "rssi": -45,
            "location": "Gate-7",
        }
    )
    response = asyncio.run(tag_reads.create_tag_read_endpoint(payload))

    assert response == {"message": "Duplicate tag ignored"}


def test_get_tag_reads_endpoint_returns_records(monkeypatch):
    expected = [
        {
            "id": 2,
            "epc": "EPC-456",
            "reader_name": "Reader B",
            "antenna": 1,
            "timestamp": "2026-05-21T10:30:00+00:00",
            "rssi": -41,
            "location": "Shelf B-02",
            "created_at": "2026-05-21T10:30:05+00:00",
        }
    ]

    fake_database = types.ModuleType("app.database")
    fake_database.create_tag_read = lambda *args, **kwargs: None
    fake_database.get_tag_reads = lambda: expected
    monkeypatch.setitem(sys.modules, "app.database", fake_database)

    module_path = Path(__file__).resolve().parents[1] / "app" / "routers" / "tag_reads.py"
    spec = importlib.util.spec_from_file_location("tag_reads_get_under_test", module_path)
    tag_reads = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(tag_reads)

    response = asyncio.run(tag_reads.get_tag_reads_endpoint())

    assert response == {"tag_reads": expected}


def test_tag_read_openapi_schema_shows_request_body_fields(monkeypatch):
    fake_database = types.ModuleType("app.database")
    fake_database.create_tag_read = lambda *args, **kwargs: None
    fake_database.get_tag_reads = lambda: []
    monkeypatch.setitem(sys.modules, "app.database", fake_database)

    module_path = Path(__file__).resolve().parents[1] / "app" / "routers" / "tag_reads.py"
    spec = importlib.util.spec_from_file_location("tag_reads_openapi_under_test", module_path)
    tag_reads = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(tag_reads)

    app = FastAPI()
    app.include_router(tag_reads.router)
    schema = app.openapi()

    request_body = schema["paths"]["/api/tagreads"]["post"]["requestBody"]
    ref = request_body["content"]["application/json"]["schema"]["$ref"]
    schema_name = ref.rsplit("/", 1)[-1]
    properties = schema["components"]["schemas"][schema_name]["properties"]

    assert set(properties) == {"epc", "readerName", "antenna", "timestamp", "rssi", "location"}
    assert set(schema["components"]["schemas"][schema_name]["required"]) == {
        "epc",
        "readerName",
        "antenna",
        "timestamp",
        "rssi",
        "location",
    }
    assert "get" in schema["paths"]["/api/tagreads"]


def test_tag_read_sql_schema_includes_location_column():
    root = Path(__file__).resolve().parents[2]
    schema_paths = [
        root / "SQL" / "schema" / "01_create_tables_postgres.sql",
        root / "SQL" / "schema" / "03_create_tag_reads.sql",
    ]

    for schema_path in schema_paths:
        sql_text = schema_path.read_text()
        assert "location    TEXT" in sql_text or "location TEXT" in sql_text
        assert "idx_tagread_dedupe" in sql_text
        assert "(epc, reader_name, antenna, timestamp)" in sql_text


def test_export_csv_endpoint(monkeypatch):
    expected = [
        {
            "id": 1,
            "epc": "EPC-1",
            "reader_name": "Reader A",
            "antenna": 2,
            "timestamp": "2026-05-28T12:00:00+00:00",
            "rssi": -45,
            "location": "Loc A",
            "created_at": "2026-05-28T12:00:05+00:00",
        }
    ]
    fake_database = types.ModuleType("app.database")
    fake_database.create_tag_read = lambda *args, **kwargs: None
    fake_database.get_tag_reads = lambda *args, **kwargs: expected
    monkeypatch.setitem(sys.modules, "app.database", fake_database)

    module_path = Path(__file__).resolve().parents[1] / "app" / "routers" / "tag_reads.py"
    spec = importlib.util.spec_from_file_location("tag_reads_export_under_test", module_path)
    tag_reads = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(tag_reads)

    response = asyncio.run(tag_reads.export_csv())
    assert response.status_code == 200
    assert response.media_type == "text/csv"
    assert b"EPC-1" in response.body
    assert b"Reader A" in response.body


def test_export_excel_endpoint(monkeypatch):
    expected = [
        {
            "id": 1,
            "epc": "EPC-1",
            "reader_name": "Reader A",
            "antenna": 2,
            "timestamp": "2026-05-28T12:00:00+00:00",
            "rssi": -45,
            "location": "Loc A",
            "created_at": "2026-05-28T12:00:05+00:00",
        }
    ]
    fake_database = types.ModuleType("app.database")
    fake_database.create_tag_read = lambda *args, **kwargs: None
    fake_database.get_tag_reads = lambda *args, **kwargs: expected
    monkeypatch.setitem(sys.modules, "app.database", fake_database)

    module_path = Path(__file__).resolve().parents[1] / "app" / "routers" / "tag_reads.py"
    spec = importlib.util.spec_from_file_location("tag_reads_export_under_test", module_path)
    tag_reads = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(tag_reads)

    response = asyncio.run(tag_reads.export_excel())
    assert response.status_code == 200
    assert response.media_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(response.body) > 0


def test_export_pdf_endpoint(monkeypatch):
    expected = [
        {
            "id": 1,
            "epc": "EPC-1",
            "reader_name": "Reader A",
            "antenna": 2,
            "timestamp": "2026-05-28T12:00:00+00:00",
            "rssi": -45,
            "location": "Loc A",
            "created_at": "2026-05-28T12:00:05+00:00",
        }
    ]
    fake_database = types.ModuleType("app.database")
    fake_database.create_tag_read = lambda *args, **kwargs: None
    fake_database.get_tag_reads = lambda *args, **kwargs: expected
    monkeypatch.setitem(sys.modules, "app.database", fake_database)

    module_path = Path(__file__).resolve().parents[1] / "app" / "routers" / "tag_reads.py"
    spec = importlib.util.spec_from_file_location("tag_reads_export_under_test", module_path)
    tag_reads = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(tag_reads)

    response = asyncio.run(tag_reads.export_pdf())
    assert response.status_code == 200
    assert response.media_type == "application/pdf"
    assert response.body.startswith(b"%PDF")
