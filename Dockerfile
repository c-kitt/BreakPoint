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

# Create data directory
RUN mkdir -p data

# Try to copy SQLite database, fall back to creating minimal one if not found
COPY data/players.db ./data/players.db || true

# Create minimal database if copy failed
RUN python3 -c "
import sqlite3, os
if not os.path.exists('./data/players.db'):
    print('Creating fallback database...')
    conn = sqlite3.connect('./data/players.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE players (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            tour TEXT NOT NULL,
            country TEXT,
            player_id TEXT
        )
    ''')
    # Insert top players
    players = [
        ('Novak Djokovic', 'Novak', 'Djokovic', 'ATP', 'SRB', '104545'),
        ('Carlos Alcaraz', 'Carlos', 'Alcaraz', 'ATP', 'ESP', '207989'),
        ('Jannik Sinner', 'Jannik', 'Sinner', 'ATP', 'ITA', '207809'),
        ('Daniil Medvedev', 'Daniil', 'Medvedev', 'ATP', 'RUS', '206948'),
        ('Rafael Nadal', 'Rafael', 'Nadal', 'ATP', 'ESP', '104745'),
        ('Iga Swiatek', 'Iga', 'Swiatek', 'WTA', 'POL', '311767'),
        ('Aryna Sabalenka', 'Aryna', 'Sabalenka', 'WTA', 'BLR', '311468'),
        ('Coco Gauff', 'Coco', 'Gauff', 'WTA', 'USA', '316364'),
        ('Jessica Pegula', 'Jessica', 'Pegula', 'WTA', 'USA', '311320'),
        ('Elena Rybakina', 'Elena', 'Rybakina', 'WTA', 'KAZ', '311648')
    ]
    for name, first, last, tour, country, pid in players:
        cursor.execute('INSERT INTO players (name, first_name, last_name, tour, country, player_id) VALUES (?, ?, ?, ?, ?, ?)', 
                      (name, first, last, tour, country, pid))
    conn.commit()
    conn.close()
    print('Fallback database created')
else:
    print('Database found, using existing one')
"

# Verify database
RUN ls -la data/players.db && echo "Final database size: $(stat -c%s data/players.db) bytes" || echo "No database found"

# Expose the port
EXPOSE 8000

# Run the Flask app
CMD ["python", "src/app.py"]