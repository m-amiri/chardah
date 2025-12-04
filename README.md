# 🕑 Chardah

> Async job-based LinkedIn profile scorer with 8-bit UI

## Stack

- Flask + ThreadPoolExecutor
- In-memory job store (no DB, no Redis)
- 8-bit retro UI with polling
- SOLID + YAGNI

## Endpoints

```
GET  /              → 8-bit UI
POST /job           → create job, returns job_id
GET  /job/<id>      → poll status (inprogress|complete|failed)
GET  /health        → healthcheck
```

## Structure

```
├── app.py              # factory
├── config.py           # env config
├── controllers/        # http handlers
├── services/           # linkedin crawler + ml model (dummy)
├── core/               # job store + runner
├── utils/              # validators
└── ui/
    ├── static/         # css + images
    └── templates/      # index.html (8-bit form)
```

## Quickstart

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5014` → use the 8-bit UI

## API

```bash
# create job
curl -X POST http://localhost:5014/job \
  -H "Content-Type: application/json" \
  -d '{"name":"John","cell_number":"989127638825","linkedin_account":"https://linkedin.com/in/johndoe"}'

# returns: {"job_id": "550e8400-..."}

# poll status
curl http://localhost:5014/job/550e8400-...

# inprogress → {"status": "inprogress"}
# complete   → {"status": "complete", "result": {...}}
# failed     → {"status": "failed"}
```

## Config

```bash
export FLASK_ENV=development
export MAX_WORKERS=4          # thread pool size
export LOG_LEVEL=INFO
```

## Design

- **Factory pattern** → app initialization
- **Dependency injection** → services loosely coupled
- **Blueprint pattern** → modular routes
- **SOLID principles** → clean separation of concerns
- **No external deps** → just Python stdlib + Flask

## Notes

- UI polls `/job/<id>` every 20s until complete/failed
- Validation: cell_number = 10-15 digits, linkedin = `/in/` profile
- Services are dummies (simulate crawl + ML inference)
- No persistence → jobs lost on restart
