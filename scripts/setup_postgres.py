#!/usr/bin/env python3
"""
Script to set up PostgreSQL database and populate with player data
"""

import psycopg2
import pandas as pd
import os
import sys
from pathlib import Path

def get_database_url():
    """Get PostgreSQL database URL from environment"""
    return os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')

def create_tables(cursor):
    """Create the players table"""
    cursor.execute('''
        DROP TABLE IF EXISTS players;
        CREATE TABLE players (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            tour VARCHAR(10) NOT NULL,
            country VARCHAR(10),
            player_id VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX idx_players_name ON players(name);
        CREATE INDEX idx_players_tour ON players(tour);
    ''')
    print("Created players table with indexes")

def populate_from_csv(cursor):
    """Populate database from CSV files"""
    base_dir = Path(__file__).parent.parent
    
    # Load ATP players
    atp_path = base_dir / 'data' / 'tennis_atp' / 'atp_players.csv'
    atp_count = 0
    
    if atp_path.exists():
        print(f"Loading ATP players from {atp_path}")
        atp_players = pd.read_csv(atp_path)
        
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
                        INSERT INTO players (name, first_name, last_name, tour, country, player_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING
                    ''', (full_name, first_name, last_name, 'ATP', country, player_id))
                    atp_count += 1
                except Exception as e:
                    print(f"Error inserting ATP player {full_name}: {e}")
        
        print(f"Inserted {atp_count} ATP players")
    else:
        print("ATP players file not found")
    
    # Load WTA players  
    wta_path = base_dir / 'data' / 'tennis_wta' / 'wta_players.csv'
    wta_count = 0
    
    if wta_path.exists():
        print(f"Loading WTA players from {wta_path}")
        wta_players = pd.read_csv(wta_path)
        
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
                        INSERT INTO players (name, first_name, last_name, tour, country, player_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING
                    ''', (full_name, first_name, last_name, 'WTA', country, player_id))
                    wta_count += 1
                except Exception as e:
                    print(f"Error inserting WTA player {full_name}: {e}")
        
        print(f"Inserted {wta_count} WTA players")
    else:
        print("WTA players file not found")
    
    return atp_count, wta_count

def setup_database():
    """Main function to set up the database"""
    database_url = get_database_url()
    
    if not database_url:
        print("ERROR: No DATABASE_URL or POSTGRES_URL environment variable found")
        print("Please set one of these environment variables with your PostgreSQL connection string")
        print("Example: postgresql://user:password@host:port/database")
        sys.exit(1)
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print(f"Connected to PostgreSQL database")
        
        # Create tables
        create_tables(cursor)
        
        # Populate from CSV files
        atp_count, wta_count = populate_from_csv(cursor)
        
        # Commit changes
        conn.commit()
        
        # Get final statistics
        cursor.execute('SELECT COUNT(*) FROM players')
        total_players = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM players WHERE tour = %s', ('ATP',))
        atp_total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM players WHERE tour = %s', ('WTA',))
        wta_total = cursor.fetchone()[0]
        
        print(f"\n✅ Database setup completed!")
        print(f"Total players: {total_players}")
        print(f"ATP players: {atp_total}")
        print(f"WTA players: {wta_total}")
        
        # Show sample data
        print("\nSample players:")
        cursor.execute('SELECT name, tour FROM players ORDER BY name LIMIT 10')
        for name, tour in cursor.fetchall():
            print(f"  {name} ({tour})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()