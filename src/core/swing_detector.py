from __future__ import annotations

import pandas as pd

from config.settings import SwingConfig
from src.indicators.atr import average_true_range


class SwingDetector:
    def __init__(self, config: SwingConfig) -> None:
        self.config = config

    def detect(self, data: pd.DataFrame) -> pd.DataFrame:
        frame = data.copy()
        frame["atr"] = average_true_range(frame, self.config.atr_period)
        frame["swing_high"] = False
        frame["swing_low"] = False
        lookback = self.config.lookback
        last_high = -10_000
        last_low = -10_000
        for position in range(lookback, len(frame) - lookback):
            window = frame.iloc[position - lookback : position + lookback + 1]
            row = frame.iloc[position]
            threshold = row["atr"] * self.config.atr_multiplier
            high_prominence = row["high"] - max(window["high"].drop(window.index[lookback], errors="ignore"))
            low_prominence = min(window["low"].drop(window.index[lookback], errors="ignore")) - row["low"]
            if high_prominence >= threshold and position - last_high >= self.config.min_distance_bars:
                frame.iat[position, frame.columns.get_loc("swing_high")] = True
                last_high = position
            if low_prominence >= threshold and position - last_low >= self.config.min_distance_bars:
                frame.iat[position, frame.columns.get_loc("swing_low")] = True
                last_low = position
        return frame
