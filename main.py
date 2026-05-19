import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from database import engine, Base
import models
from routers import auth_router
from routers import events_router
from routers import admin_router
from routers import comments_router

load_dotenv(os.path.join(backend_dir, ".env"))

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sport Events API",
    description="Backend pour la gestion d'événements sportifs",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router.router)
app.include_router(events_router.router)
app.include_router(admin_router.router)
app.include_router(comments_router.router)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
UPLOADS_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
PHOTOS_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos")
ASSETS_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "assets")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(PHOTOS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/photos", StaticFiles(directory=PHOTOS_DIR), name="photos")
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

if os.path.isdir(FRONTEND_DIR):
    for sub in ("css", "js", "pages"):
        sub_dir = os.path.join(FRONTEND_DIR, sub)
        if os.path.isdir(sub_dir):
            app.mount(f"/{sub}", StaticFiles(directory=sub_dir), name=sub)

    @app.get("/", include_in_schema=False)
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return FileResponse(os.path.join(FRONTEND_DIR, "favicon.ico"))

    @app.get("/appphoto.png", include_in_schema=False)
    def default_avatar():
        return FileResponse(os.path.join(os.path.dirname(os.path.abspath(__file__)), "appphoto.png"))

@app.get("/api/health", tags=["System"])
def health():
    return {"status": "ok", "message": "Sport Events API v2.0 🏆"}

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 8000

    print("\n" + "="*50)
    print(" SERVEUR SPORT EVENTS DEMARRE")
    print(f" Local:   http://127.0.0.1:{port}")
    print(f" Reseau:  http://{local_ip}:{port}")
    print(f" Admin:   http://127.0.0.1:{port}/pages/admin-dashboard.html")
    print("="*50 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=port)
