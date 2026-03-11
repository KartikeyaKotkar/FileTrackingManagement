from fastapi import FastAPI

from app.routers import documents, movement, versions

app = FastAPI(title="File Tracking System")

app.include_router(documents.router)
app.include_router(versions.router)
app.include_router(movement.router)


@app.get("/")
def root():
    return {"message": "File Tracking System Running"}
