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

# Create data directory and copy SQLite database
RUN mkdir -p data
COPY data/players.db ./data/

# Verify database exists
RUN ls -la data/players.db && echo "Database found: $(stat -c%s data/players.db) bytes" || echo "Database not found"

# Expose the port
EXPOSE 8000

# Run the Flask app
CMD ["python", "src/app.py"]