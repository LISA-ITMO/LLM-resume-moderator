# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync --dev

# Run locally (default port 8001)
python main.py

# Lint, format, sort imports
uv run flake8 .
uv run black .
uv run isort .

# Run E2E tests (requires running server + configured .env)
uv run pytest tests/

# Docker
docker compose up
```

Flake8 config is in `.flake8`: max line length 511, ignores I005, I001, E203, W503.

## Architecture

Two-step pipeline: resume text moderation via LLM, then education document verification via VLM (vision model).

### Request flow

1. Client uploads diploma PDFs via `POST /moderator/reserve/upload-education-file` — saved to `STORAGE_DIR`
2. Client calls `POST /moderator/reserve/selection` with `SelectionContext` (rules + full resume JSON)
3. `SelectionService` orchestrates:
   - `ResumeTextConverter` → formats resume Pydantic model into structured Russian text
   - `LLMService.moderate_resume()` → checks text against rules, returns violated rule IDs
   - For each `HigherEducation`, `LLMService.check_education()` → converts PDF pages to images (pdf2image, 150 DPI, first 3 pages), sends to VLM, extracts education metadata
   - Deletes all uploaded files after processing
4. Returns `FinalResponse` with reasoning, violated rules, per-diploma resolution, and timing

### Key files

| File | Role |
|---|---|
| `main.py` | FastAPI app, `lifespan()` init, service wiring into `app.state` |
| `configs/settings.py` | `pydantic-settings` config, `@lru_cache` singleton |
| `configs/resume_rules.json` | Default moderation rules (loaded at startup) |
| `configs/specialties.py` | Full Russian specialty classifier (~50 KB) |
| `configs/required_specialties.py` | Allowed specialty whitelist |
| `routers/schemas.py` | All Pydantic I/O models |
| `routers/api_routers.py` | Thin endpoint handlers — no business logic |
| `service/llm_service.py` | OpenAI-compatible async client (moderation + vision) |
| `service/selection_service.py` | Pipeline orchestrator |
| `service/document_service.py` | PDF validation & storage |
| `service/resume_text_converter.py` | Resume model → formatted Russian text |

### Services pattern

Services are instantiated once in `lifespan()` and stored on `app.state`. Routers access them via `request.app.state.<service>`. No dependency injection framework — direct attribute access.

### LLM integration

Both LLM calls use the OpenAI SDK pointed at `LLM_BASE_URL` (OpenAI-compatible). The model name can be overridden per-request via `SelectionContext.model`. Vision requests encode PDF pages as base64 PNG data URIs.

## Environment

Copy `.env.example` to `.env`. Required vars: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`. The `STORAGE_DIR` directory must be writable; it is volume-mounted in Docker.

## CI/CD

GitHub Actions runs lint → test → build-and-push (ghcr.io + Docker Hub) on push/PR to main. E2E tests require a `.env` secret in the repo. Docker image is `python:3.12-alpine` with `poppler-utils` (required by pdf2image).
