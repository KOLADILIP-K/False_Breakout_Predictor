from __future__ import annotations

import pandas as pd

from src.indicators.atr import average_true_range
from src.indicators.volume_profile import relative_volume


def test_atr_and_relative_volume_are_stable() -> None:
    data = pd.DataFrame({"high": [12, 13, 15], "low": [10, 11, 12], "close": [11, 12, 14], "volume": [100, 200, 300]})
    atr = average_true_range(data, period=2)
    rvol = relative_volume(data["volume"], window=2)
    assert atr.notna().all()
    assert atr.iloc[-1] > 0
    assert round(float(rvol.iloc[0]), 2) == 1.0
