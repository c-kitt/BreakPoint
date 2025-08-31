from flask import Flask, jsonify, send_from_directory, request
import pandas as pd
import psycopg2
import os
import sys
from pathlib import Path

# Add the project root to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))
from src.data_process.elo_load import EloConfig, SurfaceAwareElo

app = Flask(__name__)

# Cache for player data and Elo engine
player_data_cache = None
elo_engine = None

def load_elo_engine():
    """Load the Elo engine from processed match data"""
    global elo_engine
    
    if elo_engine is not None:
        return elo_engine
    
    try:
        # Get the base directory (one level up from src)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load the best Elo parameters
        params_path = os.path.join(base_dir, 'models', 'elo_best.txt')
        with open(params_path, 'r') as f:
            line = f.read().strip()
            # Parse: K=32, k=0.004, alpha=0.4, val_logloss=0.646084
            parts = line.split(', ')
            K = float(parts[0].split('=')[1])
            k = float(parts[1].split('=')[1])
            alpha = float(parts[2].split('=')[1])
        
        # Create config with best parameters
        config = EloConfig(K=K, k=k, alpha=alpha)
        
        # Build the Elo engine from match data
        matches_path = os.path.join(base_dir, 'results', 'matches_main.parquet')
        df = pd.read_parquet(matches_path)
        
        engine = SurfaceAwareElo(config)
        
        # Process all matches to build current ratings
        for _, row in df.iterrows():
            engine.process_match(str(row["playerA"]), str(row["playerB"]), 
                               str(row["surface"]), int(row["y"]))
        
        elo_engine = engine
        print(f"Loaded Elo engine with {len(engine.global_elo)} players")
        return engine
        
    except Exception as e:
        print(f"Error loading Elo engine: {e}")
        return None

def predict_match(engine, player1, player2, surface):
    """Predict match outcome using Elo ratings"""
    try:
        # Convert surface names to match data format
        surface_mapping = {
            'grass': 'Grass',
            'hard': 'Hard', 
            'clay': 'Clay'
        }
        surface_name = surface_mapping.get(surface.lower(), 'Hard')
        
        # Get ratings for both players
        g1, s1 = engine._get(player1, surface_name)
        g2, s2 = engine._get(player2, surface_name)
        
        # Calculate probability player1 wins
        delta = (s1 + engine.cfg.alpha * g1) - (s2 + engine.cfg.alpha * g2)
        prob_player1_wins = engine._prob_from_delta(delta)
        
        return prob_player1_wins
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return 0.5  # Default to 50/50 if error

def get_database_url():
    """Get PostgreSQL database URL from environment"""
    return os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')

def load_player_data():
    """Load and cache player data from PostgreSQL database"""
    global player_data_cache
    
    if player_data_cache is not None:
        return player_data_cache
    
    try:
        database_url = get_database_url()
        if not database_url:
            raise Exception("No DATABASE_URL or POSTGRES_URL environment variable found")
            
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get all players, ordered by name
        cursor.execute('SELECT name, tour, country, player_id FROM players ORDER BY name')
        rows = cursor.fetchall()
        
        players = []
        for name, tour, country, player_id in rows:
            players.append({
                'name': name,
                'tour': tour,
                'country': country or '',
                'player_id': player_id or ''
            })
        
        cursor.close()
        conn.close()
        
        player_data_cache = players
        print(f"Loaded {len(players)} players from PostgreSQL database")
        return players
        
    except Exception as e:
        print(f"Error loading from PostgreSQL database: {e}")
        return []

@app.route('/api/players/names')
def get_player_names():
    """API endpoint to get just player names as array"""
    players = load_player_data()
    if not players:
        return jsonify({'error': 'No players found in database'}), 500
    
    names = [player['name'] for player in players]
    response = jsonify(names)
    
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    response = jsonify({'status': 'healthy', 'service': 'tennis-prediction-api'})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/')
def home():
    """API root endpoint"""
    return jsonify({
        'service': 'BreakPoint Tennis Prediction API',
        'version': '1.0',
        'endpoints': {
            '/api/health': 'Health check',
            '/api/players/names': 'Get all player names',
            '/api/predict': 'Predict match outcome (POST)'
        }
    })

@app.route('/api/predict', methods=['POST'])
def predict_winner():
    """API endpoint to predict match winner"""
    try:
        data = request.get_json()
        player1 = data.get('player1')
        player2 = data.get('player2')
        surface = data.get('surface')
        
        if not player1 or not player2 or not surface:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Load Elo engine
        engine = load_elo_engine()
        
        if engine is None:
            return jsonify({'error': 'Prediction engine not available'}), 500
        
        # Make prediction using Elo ratings
        prob_player1_wins = predict_match(engine, player1, player2, surface)
        
        # Determine winner and confidence
        if prob_player1_wins > 0.5:
            winner = player1
            confidence = prob_player1_wins
        else:
            winner = player2
            confidence = 1 - prob_player1_wins
        
        response = jsonify({
            'winner': winner,
            'player1': player1,
            'player2': player2,
            'surface': surface,
            'confidence': round(confidence, 3)
        })
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)