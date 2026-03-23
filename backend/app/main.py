from app.routers import documents, movement, versions
from app.routers.auth import router as auth_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="File Tracking System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(documents.router)
app.include_router(versions.router)
app.include_router(movement.router)


@app.get("/")
def root():
    return {"message": "File Tracking System Running"}
