import json
import urllib.parse
from http.server import BaseHTTPRequestHandler

# Simple prediction logic for Vercel (lightweight)
PLAYER_RATINGS = {
    # Top players with basic ratings
    'Novak Djokovic': {'hard': 2100, 'clay': 2050, 'grass': 2080},
    'Carlos Alcaraz': {'hard': 2080, 'clay': 2070, 'grass': 2040},
    'Jannik Sinner': {'hard': 2070, 'clay': 2020, 'grass': 2030},
    'Daniil Medvedev': {'hard': 2060, 'clay': 1950, 'grass': 2000},
    'Rafael Nadal': {'hard': 2040, 'clay': 2150, 'grass': 1980},
    'Alexander Zverev': {'hard': 2050, 'clay': 2040, 'grass': 2010},
    'Andrey Rublev': {'hard': 2030, 'clay': 2000, 'grass': 1990},
    'Casper Ruud': {'hard': 2010, 'clay': 2060, 'grass': 1970},
    'Stefanos Tsitsipas': {'hard': 2020, 'clay': 2030, 'grass': 1980},
    'Taylor Fritz': {'hard': 2000, 'clay': 1920, 'grass': 1970},
    'Roger Federer': {'hard': 2020, 'clay': 1980, 'grass': 2100},
    'Andy Murray': {'hard': 1990, 'clay': 1970, 'grass': 2000}
}

def calculate_win_probability(rating1, rating2):
    """Calculate win probability using simplified Elo formula"""
    diff = rating1 - rating2
    return 1 / (1 + 10 ** (-diff / 400))

def get_player_rating(player_name, surface):
    """Get player rating for specific surface"""
    player_data = PLAYER_RATINGS.get(player_name)
    if not player_data:
        return 1500  # Default rating for unknown players
    
    surface_key = surface.lower()
    return player_data.get(surface_key, 1500)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            player1 = data.get('player1', '')
            player2 = data.get('player2', '')
            surface = data.get('surface', 'hard')
            
            if not player1 or not player2:
                self.send_error_response({'error': 'Missing required parameters'}, 400)
                return
            
            # Get ratings for both players on the specified surface
            rating1 = get_player_rating(player1, surface)
            rating2 = get_player_rating(player2, surface)
            
            # Calculate win probability for player1
            prob_player1_wins = calculate_win_probability(rating1, rating2)
            
            # Determine winner and confidence
            if prob_player1_wins > 0.5:
                winner = player1
                confidence = prob_player1_wins
            else:
                winner = player2
                confidence = 1 - prob_player1_wins
            
            response_data = {
                'winner': winner,
                'player1': player1,
                'player2': player2,
                'surface': surface,
                'confidence': round(confidence, 3)
            }
            
            self.send_json_response(response_data)
            
        except Exception as e:
            self.send_error_response({'error': str(e)}, 500)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(data)
        self.wfile.write(response.encode())
    
    def send_error_response(self, error_data, status=500):
        self.send_json_response(error_data, status)