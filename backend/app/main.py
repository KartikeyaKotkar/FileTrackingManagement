from app.routers import documents, movement, versions
from app.routers.auth import router as auth_router
from fastapi import FastAPI

app = FastAPI(title="File Tracking System")

app.include_router(auth_router)
app.include_router(documents.router)
app.include_router(versions.router)
app.include_router(movement.router)


@app.get("/")
def root():
    return {"message": "File Tracking System Running"}
