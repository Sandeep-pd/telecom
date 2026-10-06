# Telecom Network Intelligence Platform

This project is the first step toward a production-style telecom AI backend that monitors network quality, predicts service quality, identifies anomalies, and exposes the functionality through REST APIs.

## Phase 1: Project architecture and folder creation

This repository has been scaffolded according to a clean FastAPI + SQLAlchemy + PostgreSQL + ML architecture.

## Planned structure

- `app/` - FastAPI application source code
- `app/api/routes/` - REST endpoint modules
- `app/core/` - configuration and logging defaults
- `app/database/` - database connection and CRUD
- `app/models/` - SQLAlchemy models
- `app/schemas/` - request and response validation models
- `app/services/` - business logic layer
- `app/ml/` - preprocessing, model training, prediction, and anomaly detection modules
- `data/` - telecom measurement datasets
- `tests/` - pytest test cases

## Next phases

- Phase 1: Project architecture and folder creation
- Phase 2: PostgreSQL + SQLAlchemy setup
- Phase 3: FastAPI application and health endpoint
- Phase 4: Telecom data models and CRUD APIs
- Phase 5: ML preprocessing and model training
- Phase 6: Prediction and anomaly detection APIs
- Phase 7: Analytics and dashboards
- Phase 8: Security, validation, and deployment hardening
- Phase 9: Docker and environment orchestration
- Phase 10: Testing, CI, and production readiness

### Phase 8 status

The app now uses a lifespan-based startup, readiness endpoint, and security headers to better match production conventions.

### Phase 10 status

The project now includes a CI-ready pytest configuration with enforced coverage thresholds and a GitHub Actions workflow for automated validation.

### Phase 11 status

The UI now includes a live network overview dashboard and analytics summary endpoint that surfaces key telecom KPIs and recent measurements.

### Phase 12 status

Optional API authentication uses expiring, signed bearer tokens. It is disabled by default for the local demo (`REQUIRE_AUTH=false`); set `REQUIRE_AUTH=true`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and a unique `SECRET_KEY` in `.env` before exposing the app publicly.

Generate a signing key with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Phase 13: Live internet connection test

The UI can run an on-demand internet speed check from the user's browser. It measures latency plus download and upload throughput against Cloudflare's public speed-test service and transfers up to 6 MiB per run. The quality label is a rough guide based on latency and download speed. It measures this computer's internet performance; it does not report cellular radio metrics such as RSRP, SINR, or cell identity. Use **Run speed test** in the network overview.

### Phase 14: Live PC network details

The UI polls `/network/local-status` every five seconds and shows the host computer's adapter state, link speed, IP addresses, live per-adapter receive/transmit rates, an internet reachability probe, and (on Windows when available) Wi-Fi SSID and signal. Adapter rates are based on OS byte counters between polls. When deployed remotely, it reports the server's network, not the browser user's PC. Enable authentication before making this private network information available publicly.

### Phase 15: Live network history

The UI keeps the latest 60 five-second samples in browser-tab memory and charts aggregate receive/transmit throughput alongside internet-probe latency. The chart resets when the tab is closed or refreshed; it does not persist network history to the database.

## Local setup

```bash
cd telecom-network-intelligence
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the app

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Run with Docker Compose

```bash
docker compose up --build
```

The API will be available at http://localhost:8000 and PostgreSQL at localhost:5432.

## Notes

This is a beginner-friendly portfolio project designed to help a telecom and ML engineer explain backend design, data engineering, API development, and ML pipelines in interviews.
