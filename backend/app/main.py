import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.routes import anatomy, chat, quiz

app = FastAPI(
    title="HumanNova — AI-Powered Interactive 3D Human Atlas",
    description="Interactive 3D male and female human anatomy platform powered by Three.js and OctSem AI.",
    version="1.0.0"
)

# Configure CORS
origins = [settings.FRONTEND_ORIGIN] if settings.FRONTEND_ORIGIN != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(anatomy.router)
app.include_router(chat.router)
app.include_router(quiz.router)

# Health endpoint at root /api/health
@app.get("/api/health")
def api_health():
    return {
        "status": "online",
        "platform": "HumanNova",
        "developer": "Mohd. Almaaz Riyaz",
        "atlas_models": ["male-atlas.glb", "female-atlas.glb"],
        "ai_engine": "OctSem AI",
        "version": "1.0.0"
    }

# Serve Frontend Static Files
if settings.FRONTEND_DIR.exists():
    # Direct routes for web app pages
    @app.get("/")
    @app.get("/index.html")
    def serve_home():
        return FileResponse(settings.FRONTEND_DIR / "index.html")

    @app.get("/atlas")
    @app.get("/atlas.html")
    def serve_atlas():
        return FileResponse(settings.FRONTEND_DIR / "atlas.html")

    @app.get("/favicon.ico")
    def serve_favicon():
        logo_path = settings.FRONTEND_DIR / "assets" / "logo" / "humannova_logo.png"
        if logo_path.exists():
            return FileResponse(logo_path)
        return FileResponse(settings.FRONTEND_DIR / "index.html")

    # Explicit sub-mounts for root-relative paths used by HTML
    for sub in ["css", "js", "assets", "models"]:
        sub_path = settings.FRONTEND_DIR / sub
        if sub_path.exists():
            app.mount(f"/{sub}", StaticFiles(directory=str(sub_path)), name=sub)

    # Legacy mount for /frontend prefix
    app.mount("/frontend", StaticFiles(directory=str(settings.FRONTEND_DIR)), name="frontend")
