from __future__ import annotations

import uuid

import numpy as np
import pandas as pd

from config.settings import TrendlineConfig
from src.models.trendline import Trendline


class TrendlineDetector:
    def __init__(self, config: TrendlineConfig) -> None:
        self.config = config

    def detect(self, data: pd.DataFrame, timeframe: str) -> list[Trendline]:
        lines: list[Trendline] = []
        lines.extend(self._fit_lines(data, timeframe, "support", "swing_low", "low"))
        lines.extend(self._fit_lines(data, timeframe, "resistance", "swing_high", "high"))
        return sorted(lines, key=lambda line: line.confidence, reverse=True)[: self.config.max_lines]

    def _fit_lines(self, data: pd.DataFrame, timeframe: str, kind: str, flag: str, price_col: str) -> list[Trendline]:
        swings = data[data[flag]].tail(self.config.regression_window)
        if len(swings) < self.config.min_points:
            return []
        positions = np.array([data.index.get_loc(index) for index in swings.index], dtype=float)
        prices = swings[price_col].to_numpy(dtype=float)
        slope, intercept = np.polyfit(positions, prices, 1)
        fitted = slope * positions + intercept
        total = np.sum((prices - prices.mean()) ** 2)
        residual = np.sum((prices - fitted) ** 2)
        r_squared = float(max(0.0, 1.0 - residual / total)) if total else 1.0
        tolerance = max(float(data["atr"].mean()) * self.config.touch_tolerance_atr, 1e-9)
        distances = np.abs(prices - fitted)
        touches = int(np.sum(distances <= tolerance))
        if touches < self.config.min_points:
            return []
        confidence = round(min(100.0, (r_squared * 70.0) + min(touches, 10) * 3.0), 2)
        return [
            Trendline(
                id=f"{timeframe}-{kind}-{uuid.uuid4().hex[:8]}",
                kind=kind,
                timeframe=timeframe,
                slope=float(slope),
                intercept=float(intercept),
                r_squared=r_squared,
                touches=touches,
                start_time=swings.index.min().to_pydatetime(),
                end_time=swings.index.max().to_pydatetime(),
                confidence=confidence,
            )
        ]
