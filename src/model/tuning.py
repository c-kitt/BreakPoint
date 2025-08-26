from pathlib import Path
import pandas as pd
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from itertools import product
from sklearn.metrics import log_loss
from src.data_process.elo_load import EloConfig, add_elo_columns

IN = Path("results/matches.parquet")  
SPLIT_Y = 2021                        
SPLIT_Y2 = 2023

GRID_K = [16, 24, 32, 48]
GRID_k = [0.003, 0.004, 0.005, 0.006]
GRID_A = [0.1, 0.2, 0.3, 0.4]

def symmetric_logloss(df):
    flip = df.copy()
    flip["y"] = 0
    flip["p_elo"] = 1 - df["p_elo"]
    all_ = pd.concat([df, flip], ignore_index=True)
    return log_loss(all_["y"].astype(int), all_["p_elo"].clip(1e-6, 1-1e-6))

def main():
    raw = pd.read_parquet(IN)
    raw = raw[(raw["best_of"].isin([3,5])) & (raw["round"].isin(["R128","R64","R32","R16","QF","SF","F"]))
             & (raw["level"].isin(["G","M","A","C"]))].copy()
    raw["year"] = raw["date"].dt.year

    best = None
    for K, k, A in product(GRID_K, GRID_k, GRID_A):
        cfg = EloConfig(K=K, k=k, alpha=A)
        elo = add_elo_columns(raw, cfg)
        val = elo[(elo["year"] >= SPLIT_Y) & (elo["year"] <= SPLIT_Y2)][["p_elo","y"]].copy()
        ll = symmetric_logloss(val)
        cand = (ll, K, k, A)
        if (best is None) or (ll < best[0]): best = cand
        print(f"K={K:>2} k={k:.3f} α={A:.1f} -> logloss {ll:.4f}")

    ll, Kb, kb, Ab = best
    print(f"\nBEST: K={Kb} k={kb} α={Ab} (val logloss={ll:.4f})")

    Path("models").mkdir(parents=True, exist_ok=True)
    Path("models/elo_best.txt").write_text(f"K={Kb}, k={kb}, alpha={Ab}, val_logloss={ll:.6f}\n")

if __name__ == "__main__":
    main()
