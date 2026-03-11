from fastapi import APIRouter

from app.database import get_db, load_query

router = APIRouter(prefix="/versions", tags=["Versions"])


@router.get("/{document_id}")
def get_versions(document_id: int):

    conn = get_db()

    query = load_query("backend/sql/versions/get_versions.sql")

    rows = conn.execute(query, (document_id,)).fetchall()

    return [dict(r) for r in rows]


@router.get("/{document_id}/current")
def get_current_version(document_id: int):

    conn = get_db()

    query = load_query("backend/sql/versions/get_current_version.sql")

    row = conn.execute(query, (document_id,)).fetchone()

    return dict(row) if row else {"error": "No version found"}
