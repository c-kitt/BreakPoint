from flask import Flask, jsonify
import pandas as pd
import os
from pathlib import Path

app = Flask(__name__)

# Cache for player data
player_data_cache = None

def load_player_data():
    """Load and cache player data from ATP and WTA CSV files"""
    global player_data_cache
    
    if player_data_cache is not None:
        return player_data_cache
    
    try:
        # Get the base directory
        base_dir = Path(__file__).parent.parent
        
        # Load ATP players
        atp_path = base_dir / 'data' / 'tennis_atp' / 'atp_players.csv'
        atp_players = pd.read_csv(atp_path)
        
        # Load WTA players
        wta_path = base_dir / 'data' / 'tennis_wta' / 'wta_players.csv'
        wta_players = pd.read_csv(wta_path)
        
        players = []
        
        # Process ATP players
        for _, row in atp_players.iterrows():
            if pd.notna(row['name_first']) and pd.notna(row['name_last']):
                first_name = str(row['name_first']).strip()
                # Skip players with short first names (1-2 characters)
                if len(first_name) <= 2:
                    continue
                full_name = f"{first_name} {row['name_last']}"
                players.append(full_name)
        
        # Process WTA players
        for _, row in wta_players.iterrows():
            if pd.notna(row['name_first']) and pd.notna(row['name_last']):
                first_name = str(row['name_first']).strip()
                # Skip test entries
                if row['name_first'] == 'X' and row['name_last'] == 'X':
                    continue
                # Skip players with short first names (1-2 characters)
                if len(first_name) <= 2:
                    continue
                full_name = f"{first_name} {row['name_last']}"
                players.append(full_name)
        
        # Sort players by name and remove duplicates
        players = sorted(list(set(players)))
        
        player_data_cache = players
        return players
        
    except Exception as e:
        print(f"Error loading player data: {e}")
        return []

def handler(request):
    """Vercel serverless function handler"""
    try:
        players = load_player_data()
        return jsonify(players)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# For Vercel
def main(request):
    return handler(request)