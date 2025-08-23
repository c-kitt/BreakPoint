from pathlib import Path
import pandas as pd

LEVELS_KEEP = {"G","M","A","C"}
ROUNDS_KEEP = {"R128","R64","R32","R16","QF","SF","F"}

def filter_main_draw(df: pd.DataFrame):
    out = df[
        df["level"].isin(LEVELS_KEEP) &
        df["round"].isin(ROUNDS_KEEP) &
        (df["best_of"].isin([3,5]))
    ].copy()
    return out.reset_index(drop=True)

def main():
    IN = Path("results/matches_elo.parquet")
    OUT = Path("results/matches_main.parquet")

    df = pd.read_parquet(IN)
    df_filt = filter_main_draw(df)
    print(f"Kept {len(df_filt):,} / {len(df):,} matches")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df_filt.to_parquet(OUT, index=False)

if __name__ == "__main__":
    main()
