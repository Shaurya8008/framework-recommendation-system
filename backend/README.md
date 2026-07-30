# FrameworkFit Backend

The backend service for **FrameworkFit**, a sustainability framework recommendation system built with Python 3.11+, FastAPI, PostgreSQL, scikit-learn, XGBoost, and MLflow.

## Architecture

- **`app/`**: FastAPI REST API and PostgreSQL SQLAlchemy models (`/profiles`, `/recommend`, `/frameworks`, `/recommendations`).
- **`src/`**: 3-Stage ML Recommendation Pipeline:
  - `features.py`: Domain feature engineering (emission maturity, reporting score, compliance score, target-readiness score).
  - `candidates.py`: Stage-based candidate generation.
  - `model.py`: Multi-stage scoring (v1 rule-based -> v2 multi-class classifier -> v3 ranking layer).
  - `rerank.py`: Business logic re-ranking and prerequisite ordering (`Manage` -> `Measure` -> `Report` -> `Improve`).
  - `pipeline.py`: Unified pipeline orchestration.
  - `data_gen.py`: Synthetic dataset generator for bootstrap training.
  - `train.py`: Model training script with MLflow logging and model artifact saving.
- **`tests/`**: Pytest test suite covering feature engineering, candidates, scoring, re-ranking, API endpoints, and DB seeding.

## Running Locally

1. Create a virtual environment and install dependencies:
```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install -e .
```

2. Generate synthetic data and train ML models:
```bash
python -m src.train
```

3. Run the FastAPI development server:
```bash
uvicorn app.main:app --reload --port 8000
```

## Running with Docker Compose

```bash
docker-compose up --build
```
The API will be available at `http://localhost:8000`.
