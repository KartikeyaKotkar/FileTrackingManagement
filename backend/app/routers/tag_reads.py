from fastapi import APIRouter, HTTPException, status

from app.database import create_tag_read, get_tag_reads
from app.models.schemas import TagReadCreate

router = APIRouter(prefix="/api/tagreads", tags=["Tag Reads"])


@router.get("")
async def get_tag_reads_endpoint():
    try:
        return {"tag_reads": get_tag_reads()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_tag_read_endpoint(data: TagReadCreate):
    try:
        record = create_tag_read(
            epc=data.epc,
            reader_name=data.reader_name,
            antenna=data.antenna,
            timestamp=data.timestamp,
            rssi=data.rssi,
            location=data.location,
        )
        if record and record.get("duplicate"):
            return {"message": "Duplicate tag ignored"}

        return {
            "message": "Tag read created successfully",
            "tag_read": record,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc
