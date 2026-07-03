from __future__ import annotations

import pandas as pd


def rolling_volatility(close: pd.Series, window: int = 20) -> pd.Series:
    returns = close.pct_change().fillna(0.0)
    return returns.rolling(window=window, min_periods=2).std().fillna(0.0)
