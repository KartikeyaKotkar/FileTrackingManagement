from pydantic import BaseModel


# ----------------------------------------
# Documents
# ----------------------------------------
class DocumentCreate(BaseModel):
    reference_no: str
    title: str
    department_id: int
    created_by: int


# ----------------------------------------
# Versions
# ----------------------------------------
class VersionCreate(BaseModel):
    document_id: int
    version_no: int
    file_name: str
    file_path: str
    file_hash: str | None = None
    file_size: int | None = None
    created_by: int


# ----------------------------------------
# Movement
# ----------------------------------------
class MovementCreate(BaseModel):
    document_id: int
    from_dept: int
    to_dept: int
    movement_type: str
    approved_by: int
    moved_by: int
    remarks: str | None = None


# ----------------------------------------
# Auth / Users
# ----------------------------------------
class LoginRequest(BaseModel):
    login: str  # accepts username OR email
    password: str


class UserCreate(BaseModel):
    username: str
    fullname: str | None = None
    password: str
    email: str | None = None
    phone: str | None = None
    role_id: int | None = None
    created_by: int | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    fullname: str | None
    email: str | None
    phone: str | None
    role_id: int | None
    role_name: str | None
    is_active: int
    created_at: str | None
