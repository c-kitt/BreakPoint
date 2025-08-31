#!/usr/bin/env python3
"""
Create minimal database with top players if full database doesn't exist
"""
import sqlite3
import os

def create_minimal_database():
    db_path = './data/players.db'
    
    if os.path.exists(db_path):
        print(f'Database already exists: {os.path.getsize(db_path)} bytes')
        return
    
    print('Creating fallback database...')
    conn = sqlite3.connect(db_path)
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
        ('Alexander Zverev', 'Alexander', 'Zverev', 'ATP', 'GER', '105223'),
        ('Andrey Rublev', 'Andrey', 'Rublev', 'ATP', 'RUS', '106401'),
        ('Casper Ruud', 'Casper', 'Ruud', 'ATP', 'NOR', '207678'),
        ('Stefanos Tsitsipas', 'Stefanos', 'Tsitsipas', 'ATP', 'GRE', '207605'),
        ('Taylor Fritz', 'Taylor', 'Fritz', 'ATP', 'USA', '207371'),
        ('Roger Federer', 'Roger', 'Federer', 'ATP', 'SUI', '103819'),
        ('Andy Murray', 'Andy', 'Murray', 'ATP', 'GBR', '104918'),
        ('Iga Swiatek', 'Iga', 'Swiatek', 'WTA', 'POL', '311767'),
        ('Aryna Sabalenka', 'Aryna', 'Sabalenka', 'WTA', 'BLR', '311468'),
        ('Coco Gauff', 'Coco', 'Gauff', 'WTA', 'USA', '316364'),
        ('Jessica Pegula', 'Jessica', 'Pegula', 'WTA', 'USA', '311320'),
        ('Elena Rybakina', 'Elena', 'Rybakina', 'WTA', 'KAZ', '311648'),
        ('Ons Jabeur', 'Ons', 'Jabeur', 'WTA', 'TUN', '311476'),
        ('Marketa Vondrousova', 'Marketa', 'Vondrousova', 'WTA', 'CZE', '312142'),
        ('Karolina Muchova', 'Karolina', 'Muchova', 'WTA', 'CZE', '311766')
    ]
    
    for name, first, last, tour, country, pid in players:
        cursor.execute('''
            INSERT INTO players (name, first_name, last_name, tour, country, player_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, first, last, tour, country, pid))
    
    conn.commit()
    conn.close()
    print(f'Fallback database created with {len(players)} players')

if __name__ == "__main__":
    create_minimal_database()