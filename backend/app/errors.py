import sqlite3

from fastapi import HTTPException


def raise_for_write_error(exc: Exception, *, duplicate_detail: str) -> None:
    if isinstance(exc, sqlite3.IntegrityError):
        error = str(exc)
        if "UNIQUE constraint failed" in error:
            raise HTTPException(status_code=409, detail=duplicate_detail) from exc
        if "FOREIGN KEY constraint failed" in error:
            raise HTTPException(status_code=404, detail="Referenced record not found") from exc
        if "CHECK constraint failed" in error:
            raise HTTPException(status_code=409, detail="Invalid data for requested operation") from exc

    raise HTTPException(status_code=500, detail="Internal server error") from exc
