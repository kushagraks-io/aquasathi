# AquaSathi

A farmer-facing shrimp farm workspace for pond monitoring and incident investigation. It includes a responsive overview, pond creation, historical simulated readings, incident history, transparent threshold screening, curated source lookup, and investigation reports.

## Run locally

1. `python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -r backend/requirements.txt`
3. In one terminal, run `uvicorn backend.app.main:app --reload`.
4. In another, run `npm install && npm run dev` and open the Vite URL. The frontend proxies `/api` requests to FastAPI. `npm run build` writes a static bundle to `frontend/dist`; FastAPI serves that bundle when present.
5. API docs: http://127.0.0.1:8000/docs

SQLite is used by default. Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL to use PostgreSQL. Demo data seeds on first startup. The frontend is React + TypeScript + Vite, with Motion for screen and dialog transitions. Farmers can switch core interface labels between English, Telugu, and Hindi; the choice is stored in the browser. The Motion AI kit and UI/UX Pro Max Codex skills are installed in the project configuration folders.

## Netlify deployment

The included `netlify.toml` builds the Vite frontend and publishes `frontend/dist`, with a fallback route for the single-page app. A static Netlify deploy runs in browser demo mode when the FastAPI service is unavailable. New ponds and investigations created in that mode are saved only in that browser's local storage. The Python API and SQLite database are not hosted by this static deployment; persistent multi-user farm data requires hosting the API and database separately and configuring the frontend to use that API.

## Evidence and limits

- Lifecycle stage is stored per pond: preparation, stocking, nursery, grow-out, harvest (the demo currently seeds nursery and grow-out ponds).
- Core parameters: dissolved oxygen, temperature, pH, salinity, and total ammonia nitrogen (TAN).
- Screening examples are drawn from MPEDA SHAPHARI guidance and are not universal treatment targets. Species, stage, sampling method, time, and local conditions affect interpretation; consult a qualified aquaculture professional.
- Knowledge lookup is transparent keyword retrieval over a small curated source set, not embeddings or generative RAG.
- Investigation logic is deterministic. There is no external LLM, computer vision, or audio service. An uploaded photo filename is attached as a review note; no image is analyzed.
- Telugu/Hindi language selection is present in incident input; generated translations and speech are not yet implemented.
- Sample values are simulated and clearly marked. They are not live sensor measurements.
- No disease diagnosis, chemical dose, or treatment instruction is generated.

## Routes

`GET /api/dashboard`; `GET/POST /api/ponds`; `GET /api/ponds/{id}/readings`; `GET/POST /api/incidents`; `GET /api/knowledge/search?q=...`; `POST /api/investigate`.

## Next steps

Authentication and role access, Alembic migrations, sensor adapters, real file storage and validated vision, Indic speech services, vetted RAG ingestion/embeddings, and deployment configuration remain future phases. Review the current thresholds with an aquaculture expert before field use.
