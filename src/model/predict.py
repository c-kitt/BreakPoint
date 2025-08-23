import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
import pandas as pd
from src.data_process.elo_load import EloConfig, SurfaceAwareElo

def build_engine():
    df = pd.read_parquet("results/matches_main.parquet")
    engine = SurfaceAwareElo(EloConfig())

    for a, b, s, y in zip(df["playerA"], df["playerB"], df["surface"], df["y"]):
        engine.process_match(a, b, s, y)
    return engine

def predict(engine, playerA, playerB, surface):
    gA, sA = engine._get(playerA, surface)
    gB, sB = engine._get(playerB, surface)
    delta = (sA + engine.cfg.alpha * gA) - (sB + engine.cfg.alpha * gB)
    return engine._prob_from_delta(delta)

if __name__ == "__main__":
    engine = build_engine()
    prob = predict(engine, "Jannik Sinner", "Carlos Alcaraz", "Clay")
    print("P(Djokovic beats Alcaraz on clay): ", prob)