from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import test_connection

app = FastAPI(
    title="HTTT16 - Quan Ly Tour Du Lich",
    version="1.0.0",
    description="RESTful API quan ly tour du lich noi dia"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "HTTT16 Backend dang hoat dong"
    }


@app.get("/api/health")
def health():
    try:
        test_connection()
        return {
            "status": "success",
            "database": "connected"
        }
    except Exception:
        return {
            "status": "error",
            "database": "disconnected"
        }