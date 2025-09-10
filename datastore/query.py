from __future__ import annotations
from typing import Dict, Any, List
import pandas as pd
from .loader import DataStore

def find_best_clarity_in_theater(store: DataStore, theater: str, top_k: int = 5) -> pd.DataFrame:
    df = store.filter_and_rank_feeds(theater=theater)
    cols = ["FEED_ID","THEATER","RES_W","RES_H","FRRATE","CODEC","clarity_score"]
    return df[cols].head(top_k)

def feeds_with_constraints(store: DataStore, theater: str, min_fps: float) -> pd.DataFrame:
    df = store.list_feeds(theater=theater, min_fps=min_fps)
    return df

