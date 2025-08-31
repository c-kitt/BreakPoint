from flask import Flask, request, jsonify
import pandas as pd
import os
import sys
from pathlib import Path

# Add the project root to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.data_process.elo_load import EloConfig, SurfaceAwareElo
except ImportError:
    # Fallback if import fails
    EloConfig = None
    SurfaceAwareElo = None

app = Flask(__name__)

# Global variables for caching
elo_engine = None

def load_elo_engine():
    """Load the Elo engine from processed match data"""
    global elo_engine
    
    if elo_engine is not None:
        return elo_engine
    
    if EloConfig is None or SurfaceAwareElo is None:
        return None
    
    try:
        # Get the base directory
        base_dir = Path(__file__).parent.parent
        
        # Load the best Elo parameters
        params_path = base_dir / 'models' / 'elo_best.txt'
        with open(params_path, 'r') as f:
            line = f.read().strip()
            parts = line.split(', ')
            K = float(parts[0].split('=')[1])
            k = float(parts[1].split('=')[1])
            alpha = float(parts[2].split('=')[1])
        
        # Create config with best parameters
        config = EloConfig(K=K, k=k, alpha=alpha)
        
        # Build the Elo engine from match data
        matches_path = base_dir / 'results' / 'matches_main.parquet'
        df = pd.read_parquet(matches_path)
        
        engine = SurfaceAwareElo(config)
        
        # Process all matches to build current ratings
        for _, row in df.iterrows():
            engine.process_match(str(row["playerA"]), str(row["playerB"]), 
                               str(row["surface"]), int(row["y"]))
        
        elo_engine = engine
        return engine
        
    except Exception as e:
        print(f"Error loading Elo engine: {e}")
        return None

def predict_match(engine, player1, player2, surface):
    """Predict match outcome using Elo ratings"""
    try:
        surface_mapping = {
            'grass': 'Grass',
            'hard': 'Hard', 
            'clay': 'Clay'
        }
        surface_name = surface_mapping.get(surface.lower(), 'Hard')
        
        g1, s1 = engine._get(player1, surface_name)
        g2, s2 = engine._get(player2, surface_name)
        
        delta = (s1 + engine.cfg.alpha * g1) - (s2 + engine.cfg.alpha * g2)
        prob_player1_wins = engine._prob_from_delta(delta)
        
        return prob_player1_wins
        
    except Exception as e:
        return 0.5

def handler(request):
    """Vercel serverless function handler"""
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405
    
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
            # Fallback to random prediction if model loading fails
            import random
            winner = random.choice([player1, player2])
            confidence = 0.5
        else:
            # Make prediction using Elo ratings
            prob_player1_wins = predict_match(engine, player1, player2, surface)
            
            if prob_player1_wins > 0.5:
                winner = player1
                confidence = prob_player1_wins
            else:
                winner = player2
                confidence = 1 - prob_player1_wins
        
        return jsonify({
            'winner': winner,
            'player1': player1,
            'player2': player2,
            'surface': surface,
            'confidence': round(confidence, 3)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# For Vercel
def main(request):
    return handler(request)