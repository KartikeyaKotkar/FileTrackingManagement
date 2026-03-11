from pydantic import BaseModel


class DocumentCreate(BaseModel):
    reference_no: str
    title: str
    department_id: int
    created_by: int


class VersionCreate(BaseModel):
    document_id: int
    version_no: int
    file_name: str
    file_path: str
    file_hash: str | None = None
    file_size: int | None = None
    created_by: int


class MovementCreate(BaseModel):
    document_id: int
    from_dept: int
    to_dept: int
    movement_type: str
    approved_by: int
    moved_by: int
    remarks: str | None = None
