from __future__ import annotations
import math
from dataclasses import dataclass
from multiprocessing import Value
from pathlib import Path
from re import S
from typing import Dict, Tuple

import pandas as pd

@dataclass
class EloConfig:
    K: float = 32.0
    k: float = 0.004
    alpha: float  = 0.40
    init_rating: float = 1500.0
    unknown_surface: str = "Unknown"
    
class SurfaceAwareElo:
    def __init__(self, cfg: EloConfig):
        self.cfg = cfg

        self.global_elo: Dict[str, float] = {}
        self.surface_elo: Dict[Tuple[str, str], float] = {}

    def _get(self, player: str, surface: str):
        g = self.global_elo.get(player, self.cfg.init_rating)
        s = self.surface_elo.get((player, surface), self.cfg.init_rating)
        return g, s

    def _set(self, player: str, surface: str, g_new: float, s_new: float):
        self.global_elo[player] = g_new
        self.surface_elo[(player, surface)] = s_new
    
    def _prob_from_delta(self, delta: float):
        return 1.0 / (1.0 + math.exp(-self.cfg.k * delta))

    def process_match(self, a: str, b: str, surface: str, y: int):

        if not surface or pd.isna(surface):
            surface = self.cfg.unknown_surface

        gA, sA = self._get(a, surface)
        gB, sB = self._get(b, surface)

        blendA = sA + self.cfg.alpha * gA
        blendB = sB + self.cfg.alpha * gB
        delta = blendA - blendB

        pA = self._prob_from_delta(delta)

        K = self.cfg.K
        gA_new = gA + K * (y - pA)
        gB_new = gB + K * ((1 - y) - (1 - pA))
        sA_new = sA + K * (y - pA)
        sB_new = sB + K * ((1 - y) - (1 - pA))

        self._set(a, surface, gA_new, sA_new)
        self._set(b, surface, gB_new, sB_new)
        
        return delta, pA


def add_elo_columns(df: pd.DataFrame, cfg: EloConfig = EloConfig()):
    
    needed = {"playerA", "playerB", "surface", "y"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"Input is missing: {missing}")

    df = df.sort_values("date").reset_index(drop=True).copy()

    engine = SurfaceAwareElo(cfg)
    deltas = []
    probs = []

    for a, b, s, y in zip(df["playerA"], df["playerB"], df["surface"], df["y"]):
        delta, pA = engine.process_match(str(a), str(b), str(s) if pd.notna(s) else "", int(y))
        deltas.append(round(delta, 3))
        probs.append(pA)

    df["delta_elo_blend"] = deltas
    df["p_elo"] = probs
    return df

def main():
    IN = Path("results/matches.parquet")
    OUT = Path("results/matches_elo.parquet")

    df = pd.read_parquet(IN)
    df_out = add_elo_columns(df, EloConfig())
    OUT.parent.mkdir(parents = True, exist_ok = True)
    df_out.to_parquet(OUT, index = False)
    print(f"Processed {len(df_out)} matches -> {OUT}")

if __name__ == "__main__":
    main()







