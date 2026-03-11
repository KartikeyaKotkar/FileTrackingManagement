from fastapi import APIRouter

from app.database import create_document_with_version, fetch_all, fetch_one
from app.models.schemas import DocumentCreate
from app.sql_loader import sql

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/")
def list_documents():
    return fetch_all(sql.documents.list_documents)


@router.get("/{doc_id}")
def get_document(doc_id: int):
    return fetch_one(sql.documents.get_document, (doc_id,))


@router.post("/")
def create_document(data: DocumentCreate):

    doc_id = create_document_with_version(
        data.reference_no,
        data.title,
        data.department_id,
        data.created_by,
        {
            "version_no": 1,
            "file_name": "initial",
            "file_path": "",
            "file_hash": None,
            "file_size": None,
        },
    )

    return {"document_id": doc_id}
