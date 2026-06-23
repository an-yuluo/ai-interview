"""AI Mock Interview System — FastAPI Backend Entry Point."""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from routers import resume, interview, evaluation, history, knowledge

logger = logging.getLogger(__name__)

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
app.include_router(knowledge.router)

logger.info("All routers registered successfully")
for route in app.routes:
    logger.info(f"  Route: {getattr(route, 'methods', 'MOUNT')} {getattr(route, 'path', getattr(route, 'path_regex', '?'))}")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "AI Mock Interview"}


@app.get("/api/debug/routes")
async def debug_routes():
    """Debug endpoint: list all registered routes."""
    routes = []
    for route in app.routes:
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", str(getattr(route, "path_regex", "?")))
        routes.append({"path": path, "methods": sorted(methods) if methods else ["MOUNT"]})
    return {"routes": routes, "total": len(routes)}


# ── Serve frontend static files (production mode) ──────────────────────────
_frontend_dist = Path(__file__).parent / "frontend" / "dist"

if _frontend_dist.exists():
    # Mount static assets (js, css, images, etc.)
    app.mount("/assets", StaticFiles(directory=str(_frontend_dist / "assets")), name="static-assets")

    # Serve index.html for all non-API routes (SPA fallback)
    # IMPORTANT: API paths must NOT reach this catch-all
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Never serve SPA HTML for API paths
        if full_path.startswith("api/"):
            return JSONResponse(
                status_code=404,
                content={"detail": f"API endpoint not found: /{full_path}"},
            )
        # Try to serve the exact file first
        file_path = _frontend_dist / full_path
        if full_path and file_path.is_file():
            return FileResponse(str(file_path))
        # Fallback to index.html for SPA routing
        return FileResponse(str(_frontend_dist / "index.html"))
