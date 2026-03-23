from app.routers import documents, movement, versions, departments, files, admin
from app.routers.auth import router as auth_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.events import init_events_db

# Initialize the event DB schema
init_events_db()

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
app.include_router(departments.router)
app.include_router(files.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "File Tracking System Running"}

