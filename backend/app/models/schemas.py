from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, StrictInt, field_validator


# ----------------------------------------
# Documents
# ----------------------------------------
class DocumentCreate(BaseModel):
    reference_no: str
    tag_number: str | None = None
    title: str
    department_id: int
    created_by: int


class DocumentUpdate(BaseModel):
    reference_no: str | None = None
    tag_number: str | None = None
    title: str | None = None


class DocumentStatusUpdate(BaseModel):
    status: str


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
    role: str = "user"
    created_by: int | None = None


class UserUpdate(BaseModel):
    fullname: str | None = None
    email: str | None = None
    role: str | None = None
    is_active: int | None = None


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

class DepartmentCreate(BaseModel):
    name: str
    description: str | None = None
    created_by: int | None = None

class DepartmentUpdate(BaseModel):
    name: str
    description: str | None = None


# ----------------------------------------
# RFID Tag Reads
# ----------------------------------------
class TagReadCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    epc: str
    reader_name: str
    antenna: StrictInt
    timestamp: datetime
    rssi: StrictInt

    @field_validator("epc")
    @classmethod
    def validate_epc(cls, value: str) -> str:
        if not value:
            raise ValueError("epc cannot be empty")
        return value

    @field_validator("reader_name")
    @classmethod
    def validate_reader_name(cls, value: str) -> str:
        if not value:
            raise ValueError("reader_name cannot be empty")
        return value

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include timezone information")
        return value.astimezone(timezone.utc)
