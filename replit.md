# Krishi-Veda

An offline-first, hybrid intelligence platform for rural farmers in India. Combines modern AI (quantized TFLite models) with Vedic agricultural wisdom to provide soil health analysis and crop recommendations.

## Architecture

- **Backend**: FastAPI (Python) served via uvicorn on port 5000
- **Frontend**: Static HTML/JS PWA served by FastAPI's StaticFiles
- **Database**: SQLite (`krishi_veda_offline.db`) with farmer profiles and regional data
- **AI Models**: INT8 quantized TFLite models in `ai_models/quantized/`
- **Localization**: JSON dictionaries in `localization/dicts/` (hi, bn, ta, en)

## Project Layout

```
backend/          - FastAPI application
  main.py         - Entry point; serves frontend + API routes
  core/           - Lazy loader and data processors
  services/       - Soil health prediction service
  db/             - Database utilities
frontend/         - Static PWA (HTML/JS)
ai_models/        - Quantized TFLite models
localization/     - Multi-language JSON dictionaries
vedic_engine/     - Vedic sutra logic (Python + C++)
krishi_veda_offline.db - SQLite database
```

## Running the App

The app runs as a single FastAPI server that serves both the frontend and API:

```
uvicorn backend.main:app --host 0.0.0.0 --port 5000 --reload
```

## Key Notes

- Frontend API calls use relative URLs (`/api/v1/...`) to work through the Replit proxy
- The lazy loader (`backend/core/lazy_loader.py`) handles memory-efficient model loading
- `tensorflow-lite` is listed in requirements but not available on pip; soil inference gracefully falls back to a default score if model loading fails
- Deployment uses gunicorn: `gunicorn --bind=0.0.0.0:5000 --reuse-port backend.main:app`
