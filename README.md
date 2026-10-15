<<<<<<< HEAD
# TeleComAI

TeleComAI is a telecom fault analysis application with a FastAPI service and a
responsive network-operations dashboard. The dashboard is served from `static/`
and uses the teal theme, system light/dark mode, and the cells, prediction, and
RAG APIs described below.

## Setup and run

From the project root in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the dashboard or
`http://127.0.0.1:8000/docs` for the FastAPI documentation.

The server returns frontend settings from `/api-config.js`. Configure endpoints
and the cells fixture using environment variables; no API credentials belong
in browser code:

| Variable | Default | Purpose |
| --- | --- | --- |
| `TELCOAI_API_BASE_URL` | same origin | API origin used by the frontend |
| `TELCOAI_HEALTH_ENDPOINT` | `/health` | Prediction service health check |
| `TELCOAI_PREDICTION_ENDPOINT` | `/network/analyze` | Fault prediction |
| `TELCOAI_CELLS_ENDPOINT` | `/api/v1/cells` | Cells list and cell details |
| `TELCOAI_RAG_ASK_ENDPOINT` | `/rag/ask` | Question-answer RAG |
| `TELCOAI_RAG_STATUS_ENDPOINT` | `/rag/status` | Knowledge index status |
| `TELCOAI_USE_MOCK_CELLS` | `true` | Load the local fixture until the cells API ships |
| `TELCOAI_MOCK_CELLS_ENDPOINT` | `/static/mock-data/cells.json` | Local cells fixture |
| `TELCOAI_CORS_ORIGINS` | empty | Comma-separated browser origins allowed for cross-origin API use |

Set `TELCOAI_USE_MOCK_CELLS=false` once `GET /api/v1/cells` and
`GET /api/v1/cells/{cellId}` are available. The fixture follows the agreed API
contract and is only a UI development aid; it is not live network data. When
using a separate API origin, set `TELCOAI_API_BASE_URL` and configure that
backend's CORS policy to allow the dashboard origin.

## Prediction API

`POST /network/analyze` accepts the six metrics and a cell ID:

```json
{
  "cell_id": "CELL-1001",
  "cpu": 82,
  "traffic": 94,
  "packet_loss": 6,
  "latency": 240,
  "signal_strength": -78,
  "throughput": 90
}
```

The response contains `cell_id`, `fault`, `confidence` (0-1), `next_step`,
`alternatives` (fault/confidence pairs), and the submitted `metrics`. The
current classifier and recommendation rules are local project components;
recommendations are rule-based from `decision_agent.py`.

## Cells API contract

The live cells service is not implemented in this project yet. The dashboard
expects:

- `GET /api/v1/cells` -> `{ items, nextCursor, total }`
- `GET /api/v1/cells/{cellId}` -> one item

Each item has `id`, `name`, `updatedAt`, `metrics` (`cpu`, `traffic`, `loss`,
`lat`, `sig`, `tp`), and `prediction` (null or `fault`, `confidence`,
`predictedAt`). The dashboard derives the cells-needing-review count from
`prediction.fault !== "Healthy"`.

## RAG API

`POST /rag/ask` accepts a question with optional cell/fault context and `top_k`
(1-10, default 5):

```json
{
  "question": "Why is this cell experiencing high latency and packet loss?",
  "cell_id": "CELL-1001",
  "fault": "congestion",
  "top_k": 5
}
```

The response has `question`, `answer`, `cell_id`, `fault`, `sources`, and
`status`. Sources include the actual knowledge filename, `page` (null when
unavailable), passage content, and normalized BM25 relevance. Unknown page
numbers are not fabricated. If no matching passages exist, the API returns an
explicit insufficient-evidence status. Retrieval failures are logged server
side and return a generic 503 response.

The existing `GET /rag/search?fault=CONGESTION` endpoint and its
`{ fault, knowledge }` response are retained for compatibility.

The current RAG implementation is a local BM25 retriever over the text
knowledge file. This repository contains no configured vector database,
reranker, or LLM. Accordingly, `/rag/ask` returns cited, extractive guidance
and does not claim a confirmed root cause; a configured LLM-backed answer step
can be added when its provider and credentials are supplied.

## Tests

Run backend contract and compatibility tests:

```powershell
python -m unittest discover -s tests -v
```

With the server running, open `http://127.0.0.1:8000/static/tests.html` for
browser checks of API client contracts and severity thresholds.

## Optional radio performance monitor

The separately supplied `telecom-dashboard` monitor uses
`ws://127.0.0.1:8000/ws/metrics`. Its producer posts `snr`, `nn`, `nr`, `bn`,
`br`, `mn`, and `mb`, plus optional `insight`, to `/telemetry` once per second.
This radio telemetry feed is distinct from the network-operations dashboard
above.
=======
# 📡 Telecom Network Intelligence Platform

### ML-Based Telecom Network Quality Prediction & Anomaly Detection API

A production-oriented telecom analytics platform built using **Python, FastAPI, Machine Learning, PostgreSQL, and Docker**.

The project combines **Electronics & Telecommunication Engineering concepts** with modern backend and machine learning technologies to monitor telecom network performance, predict network quality, and detect abnormal network conditions.

---

## 🚀 Features

* 📡 Telecom network KPI monitoring
* 🤖 Machine Learning-based network quality prediction
* 🔍 Network anomaly detection
* 🐘 PostgreSQL database
* ⚡ FastAPI REST API
* 🧠 Scikit-learn / XGBoost ML models
* 🐳 Docker & Docker Compose
* 🧪 Pytest automated testing
* 📊 Network analytics
* 📝 API documentation with Swagger
* 🔐 Environment-based configuration
* ☁️ AWS EC2 deployment ready

---

## 🛠️ Technology Stack

| Technology   | Purpose               |
| ------------ | --------------------- |
| Python       | Backend & ML          |
| FastAPI      | REST API              |
| PostgreSQL   | Database              |
| SQLAlchemy   | ORM                   |
| Pydantic     | Data validation       |
| Pandas       | Data processing       |
| NumPy        | Numerical computation |
| Scikit-learn | Machine Learning      |
| XGBoost      | ML model              |
| Docker       | Containerization      |
| Pytest       | Testing               |
| Git/GitHub   | Version control       |
| AWS EC2      | Deployment            |

---

# 📂 Project Structure

```text
telecom-network-intelligence/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── network.py
│   │       ├── prediction.py
│   │       ├── anomaly.py
│   │       └── analytics.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging_config.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   └── crud.py
│   │
│   ├── models/
│   │   ├── network.py
│   │   ├── prediction.py
│   │   └── anomaly.py
│   │
│   ├── schemas/
│   │   ├── network.py
│   │   ├── prediction.py
│   │   └── anomaly.py
│   │
│   ├── services/
│   │   ├── network_service.py
│   │   ├── prediction_service.py
│   │   └── anomaly_service.py
│   │
│   └── ml/
│       ├── preprocess.py
│       ├── train.py
│       ├── predict.py
│       ├── anomaly.py
│       └── models/
│
├── data/
│   └── telecom_dataset.csv
│
├── tests/
│   ├── test_network.py
│   ├── test_prediction.py
│   └── test_anomaly.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

# 📡 Telecom KPIs

The system works with common telecom network measurements:

* RSRP
* RSRQ
* RSSI
* SINR
* Download Speed
* Upload Speed
* Latency
* Packet Loss
* Connected Users
* Call Drop Rate
* Handover Failure Rate
* Cell ID
* Region
* Network Type
* Timestamp

---

# 🤖 Machine Learning

The ML system predicts network quality based on telecom KPIs.

### Target Classes

```text
GOOD
AVERAGE
POOR
```

### Models

The project can compare:

```text
Logistic Regression
Random Forest
XGBoost
```

### Evaluation Metrics

```text
Accuracy
Precision
Recall
F1 Score
Confusion Matrix
```

The best-performing model is saved and used by the FastAPI prediction service.

---

# 🔍 Anomaly Detection

The project uses **Isolation Forest** to detect unusual network conditions.

Examples:

```text
Very low SINR
Very poor RSRP
High latency
High packet loss
High connected users
High call-drop rate
High handover-failure rate
```

Example response:

```json
{
    "is_anomaly": true,
    "anomaly_score": -0.72,
    "severity": "HIGH",
    "possible_causes": [
        "Low SINR",
        "High packet loss",
        "High latency"
    ]
}
```

---

# ⚡ FastAPI

## Install Dependencies

Create a virtual environment:

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the FastAPI Application

From the project root directory:

```bash
python -m uvicorn app.main:app --reload
```

The API will start at:

```text
http://127.0.0.1:8000
```

---

# 📚 API Documentation

After starting FastAPI, open:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

# ❤️ Health Check

Endpoint:

```http
GET /health
```

Example response:

```json
{
    "status": "healthy",
    "service": "telecom-network-intelligence"
}
```

---

# 📊 Main API Endpoints

## Network Data

### Add Network Measurement

```http
POST /network/data
```

### Get Network Measurements

```http
GET /network/data
```

### Get Specific Measurement

```http
GET /network/data/{measurement_id}
```

### Get Cell Information

```http
GET /network/cell/{cell_id}
```

---

# 🤖 Prediction

```http
POST /predict
```

Example request:

```json
{
    "rsrp": -95,
    "rsrq": -10,
    "sinr": 18,
    "download_speed": 75.2,
    "upload_speed": 18.5,
    "latency": 25,
    "packet_loss": 0.5,
    "connected_users": 80
}
```

Example response:

```json
{
    "prediction": "GOOD",
    "confidence": 0.96,
    "model_version": "1.0.0"
}
```

---

# 🔍 Anomaly Detection

```http
POST /detect-anomaly
```

The endpoint analyzes telecom KPIs and determines whether the network measurement represents an abnormal condition.

---

# 📈 Analytics

```http
GET /analytics/network
```

Example:

```json
{
    "average_latency": 34.5,
    "average_download_speed": 68.2,
    "average_packet_loss": 0.8,
    "poor_network_percentage": 12.4
}
```

---

# 🐘 PostgreSQL

The project uses PostgreSQL to store telecom measurements, predictions, and anomalies.

Example database:

```text
Database:
telecom_db

Tables:

network_measurements
predictions
anomalies
```

Database configuration is stored using environment variables.

Example `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/telecom_db
```

**Do not commit `.env` to GitHub.**

---

# 🐳 Docker

Build the Docker image:

```bash
docker build -t telecom-network-api .
```

Run the container:

```bash
docker run -p 8000:8000 telecom-network-api
```

---

# 🐳 Docker Compose

Start the complete application:

```bash
docker compose up --build
```

This starts:

```text
FastAPI
   │
   ▼
PostgreSQL
```

Stop the services:

```bash
docker compose down
```

---

# 🧪 Testing

Run all tests:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

---

# 🔄 Development Workflow

The recommended development process is:

```text
Telecom Dataset
       ↓
Data Preprocessing
       ↓
ML Training
       ↓
Model Evaluation
       ↓
Best Model
       ↓
FastAPI
       ↓
PostgreSQL
       ↓
Docker
       ↓
AWS EC2
```

---

# ☁️ Deployment Architecture

Production deployment can use:

```text
                 Internet
                    │
                    ▼
                 Nginx
                    │
                    ▼
             FastAPI Container
                    │
                    ▼
           PostgreSQL Container
```

The application can later be deployed on:

```text
AWS EC2
```

with:

```text
Docker
Nginx
HTTPS
GitHub Actions
CI/CD
```

---

# 🎯 Project Goals

This project demonstrates practical knowledge of:

### Telecom

* Cellular network KPIs
* Signal strength
* Signal quality
* Network performance
* Network anomalies
* 4G/5G concepts

### Python

* OOP
* Exception handling
* Type hints
* Modules and packages
* Logging
* Async programming

### Backend

* REST APIs
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL
* API validation
* Error handling

### Machine Learning

* Data preprocessing
* Classification
* Model comparison
* Model evaluation
* XGBoost
* Anomaly detection
* Model serialization

### DevOps

* Docker
* Docker Compose
* Git
* GitHub
* AWS EC2
* Nginx
* CI/CD

---

# 🚀 Future Improvements

Possible future features:

* Real-time telecom monitoring
* 5G KPI analytics
* Network traffic forecasting
* Cell tower failure prediction
* Time-series forecasting
* Geographical network visualization
* Streamlit dashboard
* Real telecom/network datasets
* Model monitoring
* ML model versioning
* Automated retraining
* GitHub Actions CI/CD
* HTTPS deployment

---

# 👨‍💻 Author

**Sandeep Prasad**

Electronics & Telecommunication Engineering

Interested in:

```text
Python
Backend Development
Machine Learning
Generative AI
Agentic AI
Telecom Technology
```

---

## ⭐ Project Objective

> Build a practical telecom intelligence platform that combines **Telecommunication Engineering + Python + Machine Learning + FastAPI + PostgreSQL + Docker** into a production-oriented application.

This project is designed as a portfolio and interview project demonstrating the ability to build an end-to-end ML-powered backend system.
>>>>>>> origin/main
