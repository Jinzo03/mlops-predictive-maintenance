# MLOps Predictive Maintenance

An end-to-end MLOps pipeline for predicting equipment faults from live sensor telemetry. It simulates a "Smart e-Fuse" streaming sensor data into a Postgres warehouse, trains and tracks a fault-classification model with MLflow, and serves live predictions through a FastAPI microservice — all orchestrated with Docker Compose.

## Architecture

```
Sensor Simulator ──▶ PostgreSQL (warehouse) ──▶ Model Training ──▶ MLflow (tracking & registry)
   (ingest_data.py)      (fuse_telemetry)         (train_model.py)          │
                                                                              ▼
                                                            FastAPI Prediction Service
                                                                (serve_model.py)
```

## Key Components

- **Data Ingestion** (`ingest_data.py`) — Simulates real-time telemetry (current, voltage, speed) from an e-Fuse device and streams it into a `fuse_telemetry` table in PostgreSQL, occasionally injecting simulated fault events.
- **Model Training** (`train_model.py`) — Pulls telemetry from the warehouse, trains a `RandomForestClassifier` to predict fault occurrence, and logs hyperparameters, metrics (accuracy, F1, precision, recall), and the model artifact to MLflow.
- **Model Serving** (`serve_model.py`) — A FastAPI service that loads the most recent MLflow run's model at startup and exposes a `/predict` endpoint for real-time fault inference from sensor readings.
- **Docker Compose** — Spins up the full stack: PostgreSQL (`db`), the MLflow tracking server (`mlflow_server`), and the prediction API (`api`), all on a shared network.

## Tech Stack

Python · FastAPI · scikit-learn · MLflow · PostgreSQL · Pandas · Docker Compose

## Getting Started

### Run the full stack with Docker Compose

```bash
git clone https://github.com/Jinzo03/mlops-predictive-maintenance.git
cd mlops-predictive-maintenance
docker compose up --build
```

| Service            | URL                            |
|---------------------|----------------------------------|
| Prediction API      | http://localhost:8000            |
| MLflow UI           | http://localhost:5000            |
| PostgreSQL          | localhost:5432                   |

### Generate data and train a model

The API container needs a trained model to serve, so seed data and train before (or while) it starts:

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 1. Stream simulated telemetry into Postgres (let it run for a bit to accumulate data)
python ingest_data.py

# 2. Train the model and log it to MLflow
python train_model.py
```

Once a run is logged, restart the `api` service so it picks up the trained model:

```bash
docker compose restart api
```

### Query the API

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"current": 11.8, "voltage": 219.5, "speed": 1450.0}'
```

## Project Structure

```
mlops-predictive-maintenance/
├── ingest_data.py       # Simulated sensor stream -> PostgreSQL
├── train_model.py       # Trains RandomForest and logs to MLflow
├── serve_model.py       # FastAPI inference service
├── Dockerfile            # Container image for the prediction API
├── docker-compose.yml    # Postgres + MLflow + API orchestration
└── requirements.txt
```

## Notes

The default database credentials in `docker-compose.yml` and the scripts (`admin` / `password123`) are for local development only and should be replaced before any real deployment.
