from __future__ import annotations

import pandas as pd


def true_range(data: pd.DataFrame) -> pd.Series:
    previous_close = data["close"].shift(1)
    ranges = pd.concat(
        [
            data["high"] - data["low"],
            (data["high"] - previous_close).abs(),
            (data["low"] - previous_close).abs(),
        ],
        axis=1,
    )
    return ranges.max(axis=1).fillna(data["high"] - data["low"])


def average_true_range(data: pd.DataFrame, period: int = 14) -> pd.Series:
    return true_range(data).ewm(alpha=1 / period, adjust=False, min_periods=1).mean()
