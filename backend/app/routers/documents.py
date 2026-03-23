from fastapi import APIRouter, HTTPException

from app.database import (
    create_document as create_document_record,
    fetch_all,
    fetch_one,
    update_document_status,
)
from app.errors import raise_for_write_error
from app.models.schemas import DocumentCreate, DocumentStatusUpdate
from app.sql_loader import sql

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/")
def list_documents():
    return fetch_all(sql.documents.list_documents)


@router.get("/{doc_id}")
def get_document(doc_id: int):
    document = fetch_one(sql.documents.get_document, (doc_id,))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/")
def create_document(data: DocumentCreate):
    try:
        doc_id = create_document_record(
            data.reference_no,
            data.title,
            data.department_id,
            data.created_by,
        )
        return {"document_id": doc_id}
    except Exception as e:
        raise_for_write_error(e, duplicate_detail="Reference number already exists")


@router.patch("/{doc_id}/status")
def patch_document_status(doc_id: int, data: DocumentStatusUpdate):
    try:
        updated = update_document_status(doc_id, data.status)
        if updated == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"document_id": doc_id, "status": data.status}
    except HTTPException:
        raise
    except Exception as e:
        raise_for_write_error(e, duplicate_detail="Document status update conflict")
