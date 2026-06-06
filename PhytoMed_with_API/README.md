# 🌿 PhytoMed — API Edition

Medicinal Plants & Disease Reference — now with a full REST API layer between
the UI and the database. Your PC runs as both **server** and **client**.

---

## Architecture

```
Kivy Desktop App
      │
      │  HTTP (localhost:8000)
      ▼
FastAPI Server  ──────────────────────────────────────────────
      │                  GET /search                          │
      │                  GET /diseases/{id}                   │
      │                  GET /plants/{id}                     │
      │                  GET /stats  etc.                     │
      ▼                                                       │
DatabaseService (SQLite + TF-IDF vectors)             Browser/website
```

The UI (`ApiClient`) never imports or touches the database directly.
Every call goes through HTTP — the same endpoints the website and API Explorer use.

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API server (Terminal 1)

```bash
python -m api.server
```

You'll see:
```
🌿 PhytoMed API Server starting...
   Docs:    http://localhost:8000/docs
   Website: http://localhost:8000/website/index.html
```

### 3. Start the desktop app (Terminal 2)

```bash
python main.py
```

The app connects to `http://localhost:8000` automatically.

---

## Useful URLs (once server is running)

| URL | What it is |
|-----|-----------|
| `http://localhost:8000/docs` | Interactive API explorer (Swagger UI) |
| `http://localhost:8000/website/index.html` | Project website + team page |
| `http://localhost:8000/health` | Server health check |
| `http://localhost:8000/search?q=malaria` | Example search |
| `http://localhost:8000/diseases` | All diseases list |
| `http://localhost:8000/plants` | All plants list |

---

## Project Structure

```
PhytoMed/
├── api/
│   └── server.py          ← FastAPI REST server (NEW)
├── core/
│   ├── database.py        ← SQLite + TF-IDF (unchanged)
│   └── api_client.py      ← HTTP client used by UI (NEW)
├── ui/
│   ├── app.py
│   ├── theme.py
│   ├── widgets.py
│   └── screens/
│       ├── home.py        ← uses ApiClient (updated)
│       ├── disease_detail.py  ← uses ApiClient (updated)
│       └── plant_detail.py    ← uses ApiClient (updated)
├── website/
│   ├── index.html         ← Project website + team page (NEW)
│   └── images/
│       ├── img1.jpg       ← Add team photo (Scrum Master)
│       ├── img2.jpg       ← Add team photo (Product Owner)
│       ├── img3.jpg       ← Add team photo (Backend Dev)
│       └── img4.jpg       ← Add team photo (Frontend/QA)
├── data/
│   └── medicinal_plants_vectors.db
├── assets/
├── main.py
└── requirements.txt
```

---

## Adding Team Photos

Place photos in `website/images/` as `img1.jpg`, `img2.jpg`, `img3.jpg`, `img4.jpg`.

Then in `website/index.html`, for each team card, replace the placeholder div:

```html
<!-- Remove this: -->
<div class="team-avatar-placeholder">👤</div>

<!-- Uncomment this: -->
<img class="team-avatar" src="images/img1.jpg" alt="Scrum Master">
```

---

## Changing the Server Address

If you want to run the server on a different machine or port, edit `core/api_client.py`:

```python
BASE_URL = "http://192.168.1.x:8000"   # another machine on your LAN
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health + DB stats |
| GET | `/stats` | Disease/plant/link counts |
| GET | `/search?q=&type=&top_k=` | Semantic vector search |
| GET | `/autocomplete/diseases?q=` | Disease name suggestions |
| GET | `/autocomplete/plants?q=` | Plant name suggestions |
| GET | `/diseases` | List all diseases |
| GET | `/diseases/{id}` | Full disease detail |
| GET | `/plants` | List all plants |
| GET | `/plants/{id}` | Full plant detail |
