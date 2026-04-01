from fastapi import APIRouter, Depends, HTTPException
from app.database import get_conn, fetch_all, fetch_one, move_document
from app.deps import require_admin, get_current_user_id

router = APIRouter(prefix="/transfer", tags=["Transfers"])

# Table schema should be handled by migration scripts.

@router.get("/pending")
def get_pending_transfers(_: str = Depends(require_admin)):
    query = """
        SELECT t.*, dh.title as document_title, dh.reference_no, 
               d1.name as from_department_name, d2.name as to_department_name,
               u.username as requested_by_name
        FROM transfer_request t
        JOIN document_holder dh ON t.file_id = dh.id
        LEFT JOIN department d1 ON t.from_department_id = d1.id
        LEFT JOIN department d2 ON t.to_department_id = d2.id
        LEFT JOIN app_user u ON t.requested_by = u.id
        WHERE t.status = 'pending'
        ORDER BY t.timestamp ASC
    """
    return fetch_all(query)

@router.post("/{id}/approve")
def approve_transfer(id: int, _: str = Depends(require_admin), admin_id: int = Depends(get_current_user_id)):
    req = fetch_one("SELECT * FROM transfer_request WHERE id = %s AND status = 'pending'", (id,))
    if not req:
        raise HTTPException(status_code=404, detail="Pending request not found")
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE transfer_request SET status = 'approved', approved_by = %s WHERE id = %s", (admin_id, id))
            # If tracking to_user_id in document_holder:
            if req.get("to_user_id"):
                cur.execute("UPDATE document_holder SET current_holder_user_id = %s WHERE id = %s", (req["to_user_id"], req["file_id"]))
            else:
                cur.execute("UPDATE document_holder SET current_holder_user_id = NULL WHERE id = %s", (req["file_id"],))
            conn.commit()
        
    move_document(
        document_id=req["file_id"],
        from_dept=req["from_department_id"],
        to_dept=req["to_department_id"],
        movement_type="Transfer Approved",
        approved_by=admin_id,
        moved_by=req["requested_by"],
        remarks="Admin approved transfer"
    )
    from app.database import update_document_status
    update_document_status(req["file_id"], "Active")
    return {"status": "approved"}

@router.post("/{id}/reject")
def reject_transfer(id: int, _: str = Depends(require_admin), admin_id: int = Depends(get_current_user_id)):
    req = fetch_one("SELECT * FROM transfer_request WHERE id = %s AND status = 'pending'", (id,))
    if not req:
        raise HTTPException(status_code=404, detail="Pending request not found")
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE transfer_request SET status = 'rejected', approved_by = %s WHERE id = %s", (admin_id, id))
            conn.commit()
        
    from app.database import update_document_status
    update_document_status(req["file_id"], "Active")
    return {"status": "rejected"}
