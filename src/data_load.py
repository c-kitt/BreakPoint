# src/data_load.py
import pandas as pd
from pathlib import Path
from dateutil.parser import parse

RAW_DIR_ATP = Path("data/tennis_atp")
RAW_DIR_WTA = Path("data/tennis_wtp")  # change to tennis_wta if that's your folder
OUT = Path("results/matches.parquet")

KEEP = [
    "tourney_date","tourney_name","tourney_level","surface","best_of",
    "winner_name","loser_name","round"
]

def _read_dir(d: Path, tour: str) -> pd.DataFrame:
    frames = []
    for f in sorted(d.glob("*.csv")):
        df = pd.read_csv(f, low_memory=False)
        missing = [c for c in KEEP if c not in df.columns]
        if missing:  # skip unexpected files
            continue
        df = df[KEEP].copy()
        df["tour"] = tour
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=KEEP+["tour"])

def _norm_name(s: str) -> str:
    if not isinstance(s, str):
        return s
    return " ".join(s.strip().split()).title()

def build_table() -> pd.DataFrame:
    atp = _read_dir(RAW_DIR_ATP, "ATP")
    wta = _read_dir(RAW_DIR_WTA, "WTA")
    df = pd.concat([atp, wta], ignore_index=True)

    # Parse date (Jeff’s files use YYYYMMDD integer)
    df["date"] = pd.to_datetime(df["tourney_date"].astype(str), format="%Y%m%d", errors="coerce")

    # Clean names/surface/level
    for col in ["winner_name","loser_name"]:
        df[col] = df[col].map(_norm_name)
    df["surface"] = df["surface"].str.strip().str.capitalize()  # Hard/Clay/Grass/Carpet/None
    df["tourney_level"] = df["tourney_level"].str.strip()

    # Drop rows we can’t use (missing date/names)
    df = df.dropna(subset=["date","winner_name","loser_name"])

    # Build modeling-friendly A/B sides: A = winner, label y=1
    out = pd.DataFrame({
        "date": df["date"],
        "tour": df["tour"],
        "tournament": df["tourney_name"].fillna("").str.strip(),
        "level": df["tourney_level"],
        "surface": df["surface"],
        "best_of": df["best_of"].astype("Int64"),
        "playerA": df["winner_name"],
        "playerB": df["loser_name"],
        "round": df["round"].fillna("").str.strip(),
        "y": 1,  # A won
    }).sort_values("date").reset_index(drop=True)

    return out

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table = build_table()
    table.to_parquet(OUT, index=False)
    print(f"Saved {len(table):,} matches -> {OUT}")
