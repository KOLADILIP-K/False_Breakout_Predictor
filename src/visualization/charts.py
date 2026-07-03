from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd


def candlestick_trace(data: pd.DataFrame) -> go.Candlestick:
    return go.Candlestick(
        x=data.index,
        open=data["open"],
        high=data["high"],
        low=data["low"],
        close=data["close"],
        name="OHLC",
    )
