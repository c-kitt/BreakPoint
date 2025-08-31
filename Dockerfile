FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and frontend
COPY src/ ./src/
COPY frontend/ ./frontend/

# Expose the port
EXPOSE 8000

# Run the Flask app
CMD ["python", "src/app.py"]