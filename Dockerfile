FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and frontend
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY public/ ./public/

# Copy the full SQLite database (required)
COPY data/players.db ./data/players.db

# Verify database exists and show size
RUN ls -la data/players.db && echo "Database size: $(stat -c%s data/players.db) bytes"

# Expose the port
EXPOSE 8000

# Run the Flask app
CMD ["python", "src/app.py"]