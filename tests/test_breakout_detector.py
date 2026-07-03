from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd

from config.settings import BreakoutConfig, ConfidenceConfig
from src.core.breakout_detector import FalseBreakoutDetector
from src.models.zone import Zone, ZoneType


def test_false_breakout_requires_return_inside_zone() -> None:
    index = pd.DatetimeIndex([datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=i) for i in range(6)])
    data = pd.DataFrame(
        {
            "open": [99, 101, 103, 101, 100, 99],
            "high": [101, 104, 105, 102, 101, 100],
            "low": [98, 100, 102, 99, 98, 98],
            "close": [100, 103, 104, 101, 100, 99],
            "volume": [100, 80, 70, 150, 110, 100],
            "atr": [2, 2, 2, 2, 2, 2],
        },
        index=index,
    )
    zone = Zone("z", ZoneType.RESISTANCE, 100, 102, 101, "15min", 4, index[0].to_pydatetime(), index[1].to_pydatetime(), confidence=80)
    detector = FalseBreakoutDetector(
        BreakoutConfig(lookahead_candles=3, breakout_buffer_atr=0.1, low_volume_ratio=0.95, reversal_volume_ratio=1.2, rolling_volume_window=2, trendline_tolerance_atr=0.5),
        ConfidenceConfig(60, {}),
    )
    signals = detector.detect(data, [zone], [], "15min")
    assert signals
    assert signals[0].return_bars > 0
