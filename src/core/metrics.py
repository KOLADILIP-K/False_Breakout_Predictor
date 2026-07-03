from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd


def calculate_performance(trades: pd.DataFrame) -> dict[str, Any]:
    if trades.empty:
        return {
            "total_signals": 0,
            "win_rate": 0.0,
            "loss_rate": 0.0,
            "mae": 0.0,
            "mfe": 0.0,
            "average_holding_time": 0.0,
            "average_confidence": 0.0,
            "signal_distribution": {},
        }
    wins = trades["outcome"] == "win"
    distribution = Counter(trades["signal_type"])
    return {
        "total_signals": int(len(trades)),
        "win_rate": round(float(wins.mean() * 100.0), 2),
        "loss_rate": round(float((~wins).mean() * 100.0), 2),
        "mae": round(float(trades["mae"].mean()), 4),
        "mfe": round(float(trades["mfe"].mean()), 4),
        "average_holding_time": round(float(trades["holding_bars"].mean()), 2),
        "average_confidence": round(float(trades["confidence"].mean()), 2),
        "signal_distribution": dict(distribution),
    }
