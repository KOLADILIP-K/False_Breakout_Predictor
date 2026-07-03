from __future__ import annotations

import pandas as pd


def relative_volume(volume: pd.Series, window: int = 20) -> pd.Series:
    baseline = volume.rolling(window=window, min_periods=1).mean().replace(0, pd.NA)
    return (volume / baseline).fillna(0.0)
