FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PostgreSQL, OCR, image rendering, and build tools.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications.
COPY requirements.txt pyproject.toml ./

# Install Python dependencies. Install psycopg2 explicitly because SQLAlchemy
# selects the psycopg2 PostgreSQL dialect for a postgresql:// DATABASE_URL.
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    python -m pip install --no-cache-dir "psycopg2-binary>=2.9.9" && \
    python -c "import psycopg2; print('psycopg2', psycopg2.__version__)"

# Copy application source code.
COPY . .

# Install local package in editable mode.
RUN python -m pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
