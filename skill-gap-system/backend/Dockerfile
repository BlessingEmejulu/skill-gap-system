FROM python:3.13-slim

WORKDIR /app

# Install system dependencies required for psycopg2 and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only torch first to avoid massive 500MB+ CUDA downloads timing out
RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu

RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# Copy the alembic files
COPY alembic.ini .
COPY alembic/ alembic/

# Copy the application code
COPY app/ app/

# Make sure the uploads directory exists
RUN mkdir -p uploads

EXPOSE 8001

# The startup script should apply migrations and start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8001"]
