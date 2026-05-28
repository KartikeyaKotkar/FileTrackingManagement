from fastapi import APIRouter, HTTPException, status, Response
from datetime import datetime

from app.database import create_tag_read, get_tag_reads
from app.models.schemas import TagReadCreate

router = APIRouter(prefix="/api/tagreads", tags=["Tag Reads"])


def _get_tag_reads_safe(from_date: str = None, to_date: str = None, epc: str = None, reader_name: str = None):
    try:
        return get_tag_reads(from_date=from_date, to_date=to_date, epc=epc, reader_name=reader_name)
    except TypeError as e:
        if "got an unexpected keyword argument" in str(e):
            return get_tag_reads()
        raise


@router.get("")
async def get_tag_reads_endpoint(
    from_date: str = None,
    to_date: str = None,
    epc: str = None,
    reader_name: str = None
):
    try:
        return {"tag_reads": _get_tag_reads_safe(from_date=from_date, to_date=to_date, epc=epc, reader_name=reader_name)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/export/csv")
async def export_csv(
    from_date: str = None,
    to_date: str = None,
    epc: str = None,
    reader_name: str = None
):
    try:
        records = _get_tag_reads_safe(from_date=from_date, to_date=to_date, epc=epc, reader_name=reader_name)
        from app.export_service import generate_csv
        csv_bytes = generate_csv(records)
        filename = f"tag_reads_{datetime.now().strftime('%Y-%m-%d')}.csv"
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/export/excel")
async def export_excel(
    from_date: str = None,
    to_date: str = None,
    epc: str = None,
    reader_name: str = None
):
    try:
        records = _get_tag_reads_safe(from_date=from_date, to_date=to_date, epc=epc, reader_name=reader_name)
        from app.export_service import generate_excel
        excel_bytes = generate_excel(records)
        filename = f"tag_reads_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/export/pdf")
async def export_pdf(
    from_date: str = None,
    to_date: str = None,
    epc: str = None,
    reader_name: str = None
):
    try:
        records = _get_tag_reads_safe(from_date=from_date, to_date=to_date, epc=epc, reader_name=reader_name)
        from app.export_service import generate_pdf
        pdf_bytes = generate_pdf(records)
        filename = f"tag_reads_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
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
