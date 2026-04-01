from psycopg2 import IntegrityError
from fastapi import HTTPException

def raise_for_write_error(exc: Exception, *, duplicate_detail: str) -> None:
    if isinstance(exc, IntegrityError):
        # Postgres error codes: 23505 = unique_violation, 23503 = foreign_key_violation, 23514 = check_violation
        code = exc.pgcode
        if code == '23505':
            raise HTTPException(status_code=409, detail=duplicate_detail) from exc
        if code == '23503':
            raise HTTPException(status_code=404, detail="Referenced record not found") from exc
        if code == '23514':
            raise HTTPException(status_code=409, detail="Invalid data for requested operation") from exc

    raise HTTPException(status_code=500, detail="Internal server error") from exc
