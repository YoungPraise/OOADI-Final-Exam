"""
core/database.py
────────────────
Single source of truth for all database access.
Handles both structured SQLite queries and TF-IDF vector search.
"""

import os
import sqlite3
import json
import pickle
import threading
from typing import Optional

import numpy as np
from sklearn.preprocessing import normalize

# ── Path resolution ────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_DB_PATH = os.path.join(_HERE, "..", "data", "medicinal_plants_vectors.db")


class DatabaseService:
    """
    Thread-safe singleton that manages all database operations.

    Public API
    ----------
    search(query, top_k, doc_type)  → list[SearchResult]
    get_disease(disease_id)         → DiseaseDetail
    get_plant(plant_id)             → PlantDetail
    get_all_diseases()              → list[(id, name)]
    get_all_plants()                → list[(id, english_name, latin_name)]
    autocomplete_diseases(text)     → list[(id, name)]
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst._init()
                cls._instance = inst
            return cls._instance

    # ── Initialisation ─────────────────────────────────────────────────────
    def _init(self):
        db_path = os.path.normpath(_DB_PATH)
        if not os.path.exists(db_path):
            raise FileNotFoundError(
                f"Database not found at: {db_path}\n"
                "Place medicinal_plants_vectors.db in the data/ folder."
            )
        # Use check_same_thread=False — we serialise access ourselves
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._query_lock = threading.Lock()
        self._load_vector_engine()

    def _load_vector_engine(self):
        """Load TF-IDF vectorizer + embedding matrix into memory."""
        cur = self._conn.cursor()
        row = cur.execute(
            "SELECT state FROM vectorizer_state WHERE id=1"
        ).fetchone()
        if not row:
            raise RuntimeError("vectorizer_state table is empty — wrong database?")
        self._vectorizer = pickle.loads(row[0])

        rows = cur.execute(
            "SELECT doc_type, source_id, metadata, vector FROM embeddings"
        ).fetchall()
        self._doc_types  = [r[0] for r in rows]
        self._source_ids = [r[1] for r in rows]
        self._metadata   = [json.loads(r[2]) for r in rows]
        self._matrix     = np.array(
            [np.frombuffer(r[3], dtype=np.float32) for r in rows]
        )  # (N, 8000)

    # ── Public: search ─────────────────────────────────────────────────────
    def search(
        self,
        query: str,
        top_k: int = 8,
        doc_type: Optional[str] = None,   # 'plant' | 'disease' | None
    ) -> list:
        """
        Semantic search. Returns list of dicts:
            {score, type, source_id, metadata}
        """
        if not query.strip():
            return []
        q_vec = normalize(
            self._vectorizer.transform([query]).toarray(), norm="l2"
        )[0]
        scores = self._matrix @ q_vec

        results = []
        for i in np.argsort(scores)[::-1]:
            if doc_type and self._doc_types[i] != doc_type:
                continue
            if scores[i] < 0.001:
                break
            results.append({
                "score":     float(scores[i]),
                "type":      self._doc_types[i],
                "source_id": self._source_ids[i],
                "metadata":  self._metadata[i],
            })
            if len(results) >= top_k:
                break
        return results

    # ── Public: disease detail ─────────────────────────────────────────────
    def get_disease(self, disease_id: int) -> Optional[dict]:
        """
        Returns full disease dict:
            id, name, slug, description, prevention,
            symptoms: [str],
            plants:   [plant_dict]
        """
        with self._query_lock:
            cur = self._conn.cursor()

            row = cur.execute(
                "SELECT id, name, slug, description, prevention "
                "FROM diseases WHERE id=?",
                (disease_id,)
            ).fetchone()
            if not row:
                return None
            record = dict(row)

            symptoms = cur.execute(
                "SELECT name FROM symptoms WHERE disease_id=? ORDER BY id",
                (disease_id,)
            ).fetchall()
            record["symptoms"] = [s[0] for s in symptoms]

            plants = cur.execute(
                """
                SELECT
                    p.id,
                    p.english_name,
                    p.latin_name,
                    p.description,
                    p.medicinal_use,
                    p.precautions,
                    p.toxicity,
                    p.application_steps,
                    p.location,
                    p.cameroon_location,
                    dp.part_of_plant,
                    dp.preparation_method
                FROM disease_plants dp
                JOIN plants p ON p.id = dp.plant_id
                WHERE dp.disease_id = ?
                ORDER BY p.english_name
                """,
                (disease_id,)
            ).fetchall()
            record["plants"] = [dict(p) for p in plants]
            return record

    # ── Public: plant detail ───────────────────────────────────────────────
    def get_plant(self, plant_id: int) -> Optional[dict]:
        """
        Returns full plant dict + list of diseases it treats.
        """
        with self._query_lock:
            cur = self._conn.cursor()
            row = cur.execute(
                "SELECT * FROM plants WHERE id=?", (plant_id,)
            ).fetchone()
            if not row:
                return None
            record = dict(row)

            diseases = cur.execute(
                """
                SELECT d.id, d.name, dp.part_of_plant, dp.preparation_method
                FROM disease_plants dp
                JOIN diseases d ON d.id = dp.disease_id
                WHERE dp.plant_id = ?
                ORDER BY d.name
                """,
                (plant_id,)
            ).fetchall()
            record["treats"] = [dict(d) for d in diseases]
            return record

    # ── Public: lists ──────────────────────────────────────────────────────
    def get_all_diseases(self) -> list:
        with self._query_lock:
            cur = self._conn.cursor()
            rows = cur.execute(
                "SELECT id, name FROM diseases ORDER BY name"
            ).fetchall()
            return [(r[0], r[1]) for r in rows]

    def get_all_plants(self) -> list:
        with self._query_lock:
            cur = self._conn.cursor()
            rows = cur.execute(
                "SELECT id, english_name, latin_name FROM plants "
                "ORDER BY english_name"
            ).fetchall()
            return [(r[0], r[1] or r[2], r[2]) for r in rows]

    def autocomplete_diseases(self, text: str, limit: int = 8) -> list:
        with self._query_lock:
            cur = self._conn.cursor()
            rows = cur.execute(
                "SELECT id, name FROM diseases "
                "WHERE name LIKE ? ORDER BY name LIMIT ?",
                (f"%{text}%", limit)
            ).fetchall()
            return [(r[0], r[1]) for r in rows]

    def autocomplete_plants(self, text: str, limit: int = 8) -> list:
        with self._query_lock:
            cur = self._conn.cursor()
            rows = cur.execute(
                "SELECT id, english_name, latin_name FROM plants "
                "WHERE english_name LIKE ? OR latin_name LIKE ? "
                "ORDER BY english_name LIMIT ?",
                (f"%{text}%", f"%{text}%", limit)
            ).fetchall()
            return [(r[0], r[1] or r[2], r[2]) for r in rows]

    def get_stats(self) -> dict:
        with self._query_lock:
            cur = self._conn.cursor()
            diseases = cur.execute("SELECT COUNT(*) FROM diseases").fetchone()[0]
            plants   = cur.execute("SELECT COUNT(*) FROM plants").fetchone()[0]
            links    = cur.execute("SELECT COUNT(*) FROM disease_plants").fetchone()[0]
            return {"diseases": diseases, "plants": plants, "links": links}
