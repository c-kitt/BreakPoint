FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code, frontend, and scripts
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY public/ ./public/
COPY scripts/ ./scripts/

# Create data directory
RUN mkdir -p data

# Try to copy SQLite database, create minimal one if not found
COPY data/players.db ./data/players.db 2>/dev/null || python3 scripts/create_minimal_db.py

# Verify database exists
RUN ls -la data/players.db && echo "Database size: $(stat -c%s data/players.db 2>/dev/null || echo 'unknown') bytes"

# Expose the port
EXPOSE 8000

# Run the Flask app
CMD ["python", "src/app.py"]