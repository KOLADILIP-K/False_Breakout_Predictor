from __future__ import annotations

from pathlib import Path

import pandas as pd

from config.settings import DataConfig
from src.core.data_loader import MarketDataLoader


def test_loader_cleans_duplicates_and_numeric_values(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(
        "datetime,open,high,low,close,volume,oi\n"
        "2026-01-01T09:15:00+0530,10,11,9,10.5,100,1\n"
        "2026-01-01T09:15:00+0530,10,12,9,11,120,1\n"
        "bad,10,11,9,10,100,1\n",
        encoding="utf-8",
    )
    config = DataConfig(csv_path, "datetime", "Asia/Kolkata", ["datetime", "open", "high", "low", "close", "volume", "oi"])
    data = MarketDataLoader(config, tmp_path).load()
    assert len(data) == 1
    assert data.iloc[0]["close"] == 11
    assert isinstance(data.index, pd.DatetimeIndex)
