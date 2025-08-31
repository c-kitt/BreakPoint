FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy requirements and source code
COPY requirements.txt .
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY public/ ./public/

# Copy the SQLite database (much smaller than CSV files)
COPY data/players.db ./data/players.db

# Verify database exists
RUN ls -la data/players.db && echo "Database found" || echo "Database not found"

# Expose the port
EXPOSE 8000

# Run the Flask app
CMD ["python", "src/app.py"]