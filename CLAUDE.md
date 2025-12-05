# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

```bash
# Development mode (port 5014)
python app.py

# With environment variables
export FLASK_ENV=development
export MAX_WORKERS=4
export LOG_LEVEL=INFO
export RAPIDAPI_KEY=your_rapidapi_key
export MODEL_API_URL=http://localhost:8000/score
python app.py
```

## External Dependencies

The application requires two external services:

1. **RapidAPI LinkedIn Scraper** - `https://fresh-linkedin-profile-data.p.rapidapi.com/enrich-lead`
   - API key configured via `RAPIDAPI_KEY` environment variable
   - Default key in config (for development only)

2. **ML Model Service** - `http://localhost:8000/score`
   - Scoring API endpoint configured via `MODEL_API_URL`
   - Must be running separately before starting the app

## Architecture Overview

### Application Factory Pattern

The app uses Flask's application factory in `app.py`:
- `create_app(config_name)` initializes all components
- Dependencies injected via constructor (DI pattern)
- Static/template folders point to `ui/` directory

### Core Request Flow

1. **POST /job** → `controllers/job_controller.py:create_job()`
   - Validates input via `utils/validators.py`
   - Generates UUID job_id
   - Calls `JobService.create_and_execute_job()`
   - Returns 202 with job_id immediately

2. **JobService orchestration** → `services/job_service.py:_execute_job()`
   - Creates job in JobStore with "inprogress" status
   - Submits to JobRunner (ThreadPoolExecutor)
   - Background execution:
     - Scrapes LinkedIn profile via RapidAPI
     - Maps profile data to model input format
     - Calls ML model service API for scoring
     - Updates JobStore status to "complete" or "failed"

3. **GET /job/<id>** → polls job status
   - Returns: `{"status": "inprogress|complete|failed"}`
   - If complete: includes `result` field
   - If failed: includes `error` field

### Dependency Chain

```
app.py (factory)
  → creates: JobStore, JobRunner
  → creates: LinkedInScraperService (with RapidAPI credentials)
  → creates: ModelService (with model API URL)
  → creates: JobService (injected with above)
  → creates: controller (injected with JobService)
```

### Thread Safety

- **JobStore** uses `threading.Lock()` for all operations
- **JobRunner** wraps ThreadPoolExecutor (max_workers from config)
- Important: Job runner shutdown removed from teardown to prevent premature shutdown in dev mode

## UI Integration

- **Location**: `ui/static/` (CSS, JS, images) and `ui/templates/` (HTML)
- **Main page**: GET / serves `ui/templates/index.html`
- **JavaScript**: `ui/static/app.js` handles form submission and polling
- **Polling**: UI polls GET /job/<id> every 20 seconds until complete/failed

## Validation Rules

From `utils/validators.py`:
- **name**: non-empty string (letters only in UI)
- **cell_number**: string, 10-15 digits (no +98 prefix)
- **linkedin_account**: must match `https?://linkedin.com/in/[username]`

## Configuration

Three environments in `config.py`:
- **development**: DEBUG=True (default port 5014)
- **production**: DEBUG=False
- **testing**: TESTING=True

Environment selected via `FLASK_ENV` env var or `create_app()` parameter.

## Job States

Jobs transition: `inprogress` → `complete` OR `failed`
- Status stored in `Job` dataclass (in-memory, not persisted)
- No database → jobs lost on restart

## External Services Integration

### LinkedIn Scraper Service

`LinkedInScraperService` integrates with RapidAPI to fetch real LinkedIn profile data:
- Endpoint: `https://fresh-linkedin-profile-data.p.rapidapi.com/enrich-lead`
- Returns structured profile data including:
  - Personal info (name, headline, location)
  - Work experience with company details
  - Education history
  - Connection count
- Maps raw API response to `LinkedInProfile` dataclass
- Transforms profile into model input format

### Model Service

`ModelService` calls external ML API for profile scoring:
- Endpoint: `http://localhost:8000/score` (configurable)
- Input format:
  ```json
  {
    "username": "string",
    "connections": 500,
    "worked_at": [
      {
        "company_name": "string",
        "staff_count_range": "string",
        "company_industry": "string",
        "title": "string",
        "start": "YYYY-MM-DD",
        "end": "YYYY-MM-DD" or null,
        "years": int
      }
    ],
    "studied_at": [
      {
        "school_name": "string",
        "degree_level": "string",
        "field_of_study": "string",
        "start": "YYYY-MM-DD",
        "end": "YYYY-MM-DD"
      }
    ]
  }
  ```
- Returns score, label, grade, and detailed explanation
- Response includes raw profile data in explanation field
