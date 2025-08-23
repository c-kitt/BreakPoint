from pathlib import Path
import pandas as pd 
from sklearn.metrics import log_loss, brier_score_loss, accuracy_score

def main():
    IN = Path("results/matches_main.parquet")
    df = pd.read_parquet(IN)

    df_flip = df.copy()
    df_flip["playerA"], df_flip["playerB"] = df["playerB"], df["playerA"]
    df_flip["y"] = 0
    df_flip["p_elo"] = 1 - df["p_elo"]

    df_all = pd.concat([df, df_flip], ignore_index=True)

    y_true = df_all["y"].astype(int).values
    y_pred = df_all["p_elo"].values
    
    ll = log_loss(y_true, y_pred)
    bs = brier_score_loss(y_true, y_pred)
    acc = accuracy_score(y_true, y_pred > 0.5)

    print(ll, bs, acc)

if __name__ == "__main__":
    main()