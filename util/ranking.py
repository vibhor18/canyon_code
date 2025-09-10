from __future__ import annotations
from typing import Dict
import pandas as pd

DEFAULT_WEIGHTS = {"resolution": 0.5, "fps": 0.3, "codec": 0.2}

def clarity_score_from_row(row, df: pd.DataFrame, weights: Dict[str, float] | None = None) -> float:
    wts = {**DEFAULT_WEIGHTS, **(weights or {})}
    # resolution part
    w = float(row.get("RES_W") or 0)
    h = float(row.get("RES_H") or 0)
    area = w * h
    max_area = (df["RES_W"].fillna(0) * df["RES_H"].fillna(0)).max()
    max_area = float(max_area) if pd.notna(max_area) and max_area > 0 else 1.0
    res_score = area / max_area

    # fps part
    fr = float(row.get("FRRATE") or 0)
    if "FRRATE" in df.columns:
        max_fps = pd.to_numeric(df["FRRATE"], errors="coerce").fillna(0).max()
        max_fps = float(max_fps) if max_fps and max_fps > 0 else 1.0
    else:
        max_fps = 1.0
    fps_score = fr / max_fps

    # codec part
    codec = str(row.get("CODEC") or "").upper()
    if codec in ["H265", "HEVC", "AV1"]:
        codec_bonus = 1.0
    elif codec in ["H264", "AVC", "VP9"]:
        codec_bonus = 0.9
    else:
        codec_bonus = 0.7

    return (
        wts["resolution"] * res_score
        + wts["fps"] * fps_score
        + wts["codec"] * codec_bonus
    )
