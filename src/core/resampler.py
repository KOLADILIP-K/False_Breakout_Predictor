from __future__ import annotations

import pandas as pd


class MarketDataResampler:
    aggregation = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "oi": "last",
    }

    def resample(self, data: pd.DataFrame, rule: str) -> pd.DataFrame:
        available = {key: value for key, value in self.aggregation.items() if key in data.columns}
        frame = data.resample(rule).agg(available).dropna(subset=["open", "high", "low", "close"])
        if "volume" in frame:
            frame["volume"] = frame["volume"].fillna(0.0)
        if "oi" in frame:
            frame["oi"] = frame["oi"].ffill().fillna(0.0)
        return frame

    def multi_timeframe(self, data: pd.DataFrame, rules: dict[str, str]) -> dict[str, pd.DataFrame]:
        return {name: self.resample(data, rule) for name, rule in rules.items()}
