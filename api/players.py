from flask import Flask, jsonify
import json

app = Flask(__name__)

# Curated list of top tennis players for Vercel (lightweight)
PLAYERS = [
    "Novak Djokovic",
    "Carlos Alcaraz", 
    "Jannik Sinner",
    "Daniil Medvedev",
    "Rafael Nadal",
    "Alexander Zverev",
    "Andrey Rublev",
    "Casper Ruud",
    "Stefanos Tsitsipas",
    "Taylor Fritz",
    "Tommy Paul",
    "Alex de Minaur",
    "Grigor Dimitrov",
    "Hubert Hurkacz",
    "Ben Shelton",
    "Frances Tiafoe",
    "Lorenzo Musetti",
    "Sebastian Korda",
    "Holger Rune",
    "Ugo Humbert",
    "Roger Federer",
    "Andy Murray",
    "Stan Wawrinka",
    "Marin Cilic",
    "Dominic Thiem",
    "Karen Khachanov",
    "Felix Auger-Aliassime",
    "Matteo Berrettini",
    "Cameron Norrie",
    "Denis Shapovalov",
    "Nick Kyrgios",
    "Gael Monfils",
    "Roberto Bautista Agut",
    "Pablo Carreno Busta",
    "Diego Schwartzman",
    "John Isner",
    "Reilly Opelka",
    "Milos Raonic",
    "Kei Nishikori",
    "David Goffin",
    # Top WTA players
    "Iga Swiatek",
    "Aryna Sabalenka", 
    "Coco Gauff",
    "Jessica Pegula",
    "Elena Rybakina",
    "Ons Jabeur",
    "Marketa Vondrousova",
    "Karolina Muchova",
    "Maria Sakkari",
    "Barbora Krejcikova",
    "Petra Kvitova",
    "Caroline Wozniacki",
    "Madison Keys",
    "Elise Mertens",
    "Victoria Azarenka",
    "Belinda Bencic",
    "Emma Raducanu",
    "Leylah Fernandez",
    "Naomi Osaka",
    "Simona Halep",
    "Bianca Andreescu",
    "Garbiñe Muguruza",
    "Angelique Kerber",
    "Serena Williams",
    "Venus Williams"
]

def handler(request):
    """Vercel serverless function handler"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        return jsonify(sorted(PLAYERS))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# For Vercel
def main(request):
    return handler(request)