from fastapi import APIRouter, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from app.database import create_tag_read
from app.models.schemas import TagReadCreate

router = APIRouter(prefix="/api/tagreads", tags=["Tag Reads"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_tag_read_endpoint(request: Request):
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    try:
        data = TagReadCreate.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail=jsonable_encoder(exc.errors()),
        ) from exc

    try:
        record = create_tag_read(
            epc=data.epc,
            reader_name=data.reader_name,
            antenna=data.antenna,
            timestamp=data.timestamp,
            rssi=data.rssi,
        )
        return {
            "message": "Tag read created successfully",
            "tag_read": record,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc
