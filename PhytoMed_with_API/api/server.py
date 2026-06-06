"""
api/server.py
─────────────
PhytoMed REST API Server — run with:
    python -m api.server
    OR: uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

All UI communication now goes through HTTP — the desktop client never
touches the database directly.
"""

import os
import sys

# Make sure imports resolve from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional

from core.database import DatabaseService

# ── App setup ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="PhytoMed API",
    description="Medicinal Plants & Disease Reference — REST backend",
    version="2.0.0",
)

# Allow the Kivy desktop client (and browser) on same machine to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # fine for local LAN use; restrict in production
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Serve the website under /website
_WEBSITE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "website")
if os.path.isdir(_WEBSITE_DIR):
    app.mount("/website", StaticFiles(directory=_WEBSITE_DIR, html=True), name="website")

# Singleton DB service
db = DatabaseService()


# ── Health ─────────────────────────────────────────────────────────────────
@app.get("/", tags=["meta"])
def root():
    return {"service": "PhytoMed API", "version": "2.0.0", "status": "ok"}


@app.get("/health", tags=["meta"])
def health():
    stats = db.get_stats()
    return {"status": "ok", **stats}


# ── Stats ──────────────────────────────────────────────────────────────────
@app.get("/stats", tags=["meta"])
def get_stats():
    return db.get_stats()


# ── Search ─────────────────────────────────────────────────────────────────
@app.get("/search", tags=["search"])
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(12, ge=1, le=50),
    type: Optional[str] = Query(None, description="Filter: 'plant' | 'disease'"),
):
    """
    Semantic TF-IDF vector search across plants and diseases.
    Returns ranked list of matches with score and metadata.
    """
    results = db.search(q, top_k=top_k, doc_type=type)
    return {"query": q, "count": len(results), "results": results}


# ── Autocomplete ───────────────────────────────────────────────────────────
@app.get("/autocomplete/diseases", tags=["search"])
def autocomplete_diseases(q: str = Query(..., min_length=1), limit: int = 8):
    rows = db.autocomplete_diseases(q, limit)
    return [{"id": r[0], "name": r[1]} for r in rows]


@app.get("/autocomplete/plants", tags=["search"])
def autocomplete_plants(q: str = Query(..., min_length=1), limit: int = 8):
    rows = db.autocomplete_plants(q, limit)
    return [{"id": r[0], "name": r[1], "latin_name": r[2]} for r in rows]


# ── Diseases ───────────────────────────────────────────────────────────────
@app.get("/diseases", tags=["diseases"])
def list_diseases():
    rows = db.get_all_diseases()
    return [{"id": r[0], "name": r[1]} for r in rows]


@app.get("/diseases/{disease_id}", tags=["diseases"])
def get_disease(disease_id: int):
    data = db.get_disease(disease_id)
    if not data:
        raise HTTPException(status_code=404, detail="Disease not found")
    return data


# ── Plants ─────────────────────────────────────────────────────────────────
@app.get("/plants", tags=["plants"])
def list_plants():
    rows = db.get_all_plants()
    return [{"id": r[0], "name": r[1], "latin_name": r[2]} for r in rows]


@app.get("/plants/{plant_id}", tags=["plants"])
def get_plant(plant_id: int):
    data = db.get_plant(plant_id)
    if not data:
        raise HTTPException(status_code=404, detail="Plant not found")
    return data


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("\n🌿 PhytoMed API Server starting...")
    print("   Docs:    http://localhost:8000/docs")
    print("   Website: http://localhost:8000/website/index.html\n")
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
