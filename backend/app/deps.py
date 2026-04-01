from fastapi import Header, HTTPException, Depends

def get_current_user_role(x_user_role: str = Header(default="user")):
    return x_user_role

def get_current_user_id(x_user_id: int = Header(default=0)):
    return x_user_id

def get_current_user_dept(x_user_dept_id: str = Header(default="")):
    return int(x_user_dept_id) if x_user_dept_id.isdigit() else 0

def require_admin(role: str = Depends(get_current_user_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")
    return role

def check_file_access(role: str, user_dept_id: int, file_dept_id: int):
    if role == "admin":
        return True
    if user_dept_id != file_dept_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only access files in your assigned department")
    return True
