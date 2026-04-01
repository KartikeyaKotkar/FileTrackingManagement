from fastapi import APIRouter, HTTPException, Depends

from app.database import add_version, fetch_all, fetch_one
from app.errors import raise_for_write_error
from app.models.schemas import VersionCreate
from app.sql_loader import sql
from app.deps import get_current_user_role, get_current_user_dept, check_file_access

router = APIRouter(prefix="/versions", tags=["Versions"])


@router.get("/{document_id}")
def get_versions(document_id: int, role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept)):
    document = fetch_one("SELECT department_id FROM document_holder WHERE id = %s", (document_id,))
    if document:
        check_file_access(role, dept_id, document["department_id"])
    return fetch_all(sql.versions.get_versions, (document_id,))


@router.get("/{document_id}/current")
def get_current_version(document_id: int, role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept)):
    document = fetch_one("SELECT department_id FROM document_holder WHERE id = %s", (document_id,))
    if document:
        check_file_access(role, dept_id, document["department_id"])

    version = fetch_one(sql.versions.get_current_version, (document_id,))
    if not version:
        raise HTTPException(status_code=404, detail="Current version not found")
    return version


@router.post("/")
def create_version(data: VersionCreate, role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept)):
    document = fetch_one("SELECT department_id FROM document_holder WHERE id = %s", (data.document_id,))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    check_file_access(role, dept_id, document["department_id"])

    try:
        version_id = add_version(
            data.document_id,
            data.version_no,
            data.file_name,
            data.file_path,
            data.file_hash,
            data.file_size,
            data.created_by,
        )
        return {"version_id": version_id}
    except Exception as e:
        raise_for_write_error(
            e,
            duplicate_detail="Version number already exists for this document",
        )
