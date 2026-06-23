"""AI Mock Interview System — FastAPI Backend Entry Point."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routers import resume, interview, evaluation, history

app = FastAPI(
    title="AI 模拟面试系统",
    description="AI-powered mock interview assistant",
    version="1.0.0",
)

# CORS — allow all origins (development + tunnel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(resume.router)
app.include_router(interview.router)
app.include_router(evaluation.router)
app.include_router(history.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "AI Mock Interview"}


# ── Serve frontend static files (production mode) ──────────────────────────
_frontend_dist = Path(__file__).parent / "frontend" / "dist"

if _frontend_dist.exists():
    # Mount static assets (js, css, images, etc.)
    app.mount("/assets", StaticFiles(directory=str(_frontend_dist / "assets")), name="static-assets")

    # Serve index.html for all non-API routes (SPA fallback)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Try to serve the exact file first
        file_path = _frontend_dist / full_path
        if full_path and file_path.is_file():
            return FileResponse(str(file_path))
        # Fallback to index.html for SPA routing
        return FileResponse(str(_frontend_dist / "index.html"))
