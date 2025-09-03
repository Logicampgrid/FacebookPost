#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

FRONTEND_BUILD_DIR = "/app/frontend/build"

# Mount static files
if os.path.exists(f"{FRONTEND_BUILD_DIR}/static"):
    app.mount("/static", StaticFiles(directory=f"{FRONTEND_BUILD_DIR}/static"), name="static")
    print("✅ Static files mounted")

@app.get("/api/test")
async def test_api():
    return {"message": "API works"}

@app.get("/")
async def serve_root():
    """Serve React app at root"""
    index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"error": "index.html not found"}

@app.get("/{path:path}")
async def serve_spa(path: str):
    """Serve SPA for all other routes"""
    # Skip API routes
    if path.startswith("api/"):
        return {"error": "API endpoint not found"}
    
    # Try to serve specific file first
    file_path = os.path.join(FRONTEND_BUILD_DIR, path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # For SPA routing, serve index.html
    index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"error": "Frontend not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)