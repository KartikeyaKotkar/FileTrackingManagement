from fastapi import Header, HTTPException, Depends

def get_current_user_role(x_user_role: str = Header(default="user")):
    return x_user_role

def require_admin(role: str = Depends(get_current_user_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")
    return role
