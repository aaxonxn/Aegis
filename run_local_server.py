"""
Local Development Server for Aegis Vercel Deployment.
Mounts the FastAPI serverless API (/api) and static frontend dashboard (/public)
to emulate the production Vercel runtime locally.
"""

import os
import sys
import uvicorn
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from api.index import app

# Mount public directory for local testing
public_dir = os.path.join(BASE_DIR, "public")
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Aegis Local Server on http://localhost:{port}")
    print("Serving Vercel Serverless API on /api and Dashboard on /")
    uvicorn.run("run_local_server:app", host="127.0.0.1", port=port, reload=False)

