from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from config.settings import DataConfig

LOGGER = logging.getLogger(__name__)


class MarketDataLoader:
    def __init__(self, config: DataConfig, project_root: Path) -> None:
        self.config = config
        self.project_root = project_root

    def load(self) -> pd.DataFrame:
        path = self.config.input_path if self.config.input_path.is_absolute() else self.project_root / self.config.input_path
        LOGGER.info("Loading market data from %s", path)
        data = pd.read_csv(path)
        self._validate_columns(data)
        return self.clean(data)

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        frame = data.copy()
        frame[self.config.datetime_column] = pd.to_datetime(frame[self.config.datetime_column], errors="coerce", utc=True)
        frame = frame.dropna(subset=[self.config.datetime_column])
        frame = frame.sort_values(self.config.datetime_column)
        keep = "last" if self.config.duplicate_policy == "last" else "first"
        frame = frame.drop_duplicates(subset=[self.config.datetime_column], keep=keep)
        numeric_columns = [column for column in self.config.required_columns if column != self.config.datetime_column]
        for column in numeric_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame[numeric_columns] = frame[numeric_columns].ffill().bfill()
        frame = frame.set_index(self.config.datetime_column)
        frame.index.name = "datetime"
        frame = frame[~frame.index.duplicated(keep=keep)]
        frame = frame.dropna(subset=["open", "high", "low", "close"])
        if "volume" in frame:
            frame["volume"] = frame["volume"].clip(lower=0)
        if "oi" in frame:
            frame["oi"] = frame["oi"].clip(lower=0)
        LOGGER.info("Loaded %d cleaned rows", len(frame))
        return frame

    def _validate_columns(self, data: pd.DataFrame) -> None:
        missing = set(self.config.required_columns) - set(data.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
