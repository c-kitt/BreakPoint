#!/usr/bin/env python3
"""
Script to create SQLite database from ATP/WTA CSV files
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

def create_player_database():
    # Get paths
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / 'data' / 'players.db'
    
    # Create data directory if it doesn't exist
    db_path.parent.mkdir(exist_ok=True)
    
    # Remove existing database
    if db_path.exists():
        db_path.unlink()
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create players table
    cursor.execute('''
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            tour TEXT NOT NULL,
            country TEXT,
            player_id TEXT
        )
    ''')
    
    print("Created players table...")
    
    # Load ATP players
    atp_path = base_dir / 'data' / 'tennis_atp' / 'atp_players.csv'
    if atp_path.exists():
        print(f"Loading ATP players from {atp_path}")
        atp_players = pd.read_csv(atp_path)
        
        atp_count = 0
        for _, row in atp_players.iterrows():
            if pd.notna(row['name_first']) and pd.notna(row['name_last']):
                first_name = str(row['name_first']).strip()
                last_name = str(row['name_last']).strip()
                
                # Skip players with short first names (1-2 characters)
                if len(first_name) <= 2:
                    continue
                    
                full_name = f"{first_name} {last_name}"
                country = str(row.get('ioc', '')) if pd.notna(row.get('ioc')) else ''
                player_id = str(row['player_id']) if pd.notna(row['player_id']) else ''
                
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO players (name, first_name, last_name, tour, country, player_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (full_name, first_name, last_name, 'ATP', country, player_id))
                    atp_count += 1
                except sqlite3.Error as e:
                    print(f"Error inserting ATP player {full_name}: {e}")
        
        print(f"Inserted {atp_count} ATP players")
    else:
        print("ATP players file not found")
    
    # Load WTA players
    wta_path = base_dir / 'data' / 'tennis_wta' / 'wta_players.csv'
    if wta_path.exists():
        print(f"Loading WTA players from {wta_path}")
        wta_players = pd.read_csv(wta_path)
        
        wta_count = 0
        for _, row in wta_players.iterrows():
            if pd.notna(row['name_first']) and pd.notna(row['name_last']):
                first_name = str(row['name_first']).strip()
                last_name = str(row['name_last']).strip()
                
                # Skip test entries
                if first_name == 'X' and last_name == 'X':
                    continue
                    
                # Skip players with short first names (1-2 characters)
                if len(first_name) <= 2:
                    continue
                    
                full_name = f"{first_name} {last_name}"
                country = str(row.get('ioc', '')) if pd.notna(row.get('ioc')) else ''
                player_id = str(row['player_id']) if pd.notna(row['player_id']) else ''
                
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO players (name, first_name, last_name, tour, country, player_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (full_name, first_name, last_name, 'WTA', country, player_id))
                    wta_count += 1
                except sqlite3.Error as e:
                    print(f"Error inserting WTA player {full_name}: {e}")
        
        print(f"Inserted {wta_count} WTA players")
    else:
        print("WTA players file not found")
    
    # Commit and get final count
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM players')
    total_players = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM players WHERE tour = "ATP"')
    atp_total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM players WHERE tour = "WTA"')
    wta_total = cursor.fetchone()[0]
    
    print(f"\nDatabase created successfully!")
    print(f"Total players: {total_players}")
    print(f"ATP players: {atp_total}")
    print(f"WTA players: {wta_total}")
    print(f"Database size: {db_path.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"Database location: {db_path}")
    
    # Show some sample data
    print("\nSample players:")
    cursor.execute('SELECT name, tour FROM players ORDER BY name LIMIT 10')
    for name, tour in cursor.fetchall():
        print(f"  {name} ({tour})")
    
    conn.close()
    return db_path

if __name__ == "__main__":
    create_player_database()