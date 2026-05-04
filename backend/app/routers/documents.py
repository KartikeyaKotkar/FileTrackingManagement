from fastapi import APIRouter, HTTPException, Depends

from app.database import (
    create_document as create_document_record,
    fetch_all,
    fetch_one,
    update_document_status,
    update_document as update_document_record,
)
from app.errors import raise_for_write_error
from app.models.schemas import DocumentCreate, DocumentStatusUpdate, DocumentUpdate
from app.sql_loader import sql
from app.deps import get_current_user_role, get_current_user_dept, check_file_access

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/")
def list_documents(role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept)):
    query = """
        SELECT dh.*, d.name as department_name 
        FROM document_holder dh
        LEFT JOIN department d ON dh.department_id = d.id
        ORDER BY dh.created_at DESC
    """
    docs = fetch_all(query)
    if role != "admin":
        docs = [d for d in docs if d["department_id"] == dept_id]
        
    for d in docs:
        d["department"] = {"id": d["department_id"], "name": d["department_name"]}
    return docs

@router.get("/{doc_id}")
def get_document(doc_id: int, role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept)):
    query = """
        SELECT dh.*, d.name as department_name 
        FROM document_holder dh
        LEFT JOIN department d ON dh.department_id = d.id
        WHERE dh.id = %s
    """
    document = fetch_one(query, (doc_id,))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    check_file_access(role, dept_id, document["department_id"])
    
    d = dict(document)
    d["department"] = {"id": d["department_id"], "name": d["department_name"]}
    return d


@router.post("/")
def create_document(data: DocumentCreate, role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept)):
    if role != "admin":
        data.department_id = dept_id
    try:
        doc_id = create_document_record(
            data.reference_no,
            data.tag_number,
            data.title,
            data.department_id,
            data.created_by,
        )
        return {"document_id": doc_id}
    except Exception as e:
        raise_for_write_error(e, duplicate_detail="Reference number already exists")


@router.patch("/{doc_id}/status")
def patch_document_status(doc_id: int, data: DocumentStatusUpdate, role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept)):
    document = fetch_one(sql.documents.get_document, (doc_id,))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    check_file_access(role, dept_id, document["department_id"])
    
    try:
        updated = update_document_status(doc_id, data.status)
        if updated == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"document_id": doc_id, "status": data.status}
    except HTTPException:
        raise
    except Exception as e:
        raise_for_write_error(e, duplicate_detail="Document status update conflict")


@router.put("/{doc_id}")
def update_document(doc_id: int, data: DocumentUpdate, role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept)):
    document = fetch_one(sql.documents.get_document, (doc_id,))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Optional: ensure user is owner or admin to edit full document info
    if role != "admin" and document["department_id"] != dept_id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this document")
    
    try:
        updated = update_document_record(
            doc_id,
            data.reference_no,
            data.tag_number,
            data.title
        )
        if updated == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"document_id": doc_id, "updated": True}
    except Exception as e:
        raise_for_write_error(e, duplicate_detail="Reference number already exists")
