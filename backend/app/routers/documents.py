from fastapi import APIRouter

from app.database import fetch_all, fetch_one
from app.sql_loader import sql

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/")
def list_documents():
    return fetch_all(sql.documents.list_documents)


@router.get("/{doc_id}")
def get_document(doc_id: int):
    return fetch_one(sql.documents.get_document, (doc_id,))
