from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DataConfig:
    input_path: Path
    datetime_column: str
    timezone: str
    required_columns: list[str]
    duplicate_policy: str = "last"


@dataclass(frozen=True)
class TimeframeConfig:
    name: str
    rule: str
    weight: float


@dataclass(frozen=True)
class ResamplingConfig:
    base_timeframe: str
    timeframes: list[TimeframeConfig]


@dataclass(frozen=True)
class SwingConfig:
    lookback: int
    atr_period: int
    atr_multiplier: float
    min_distance_bars: int


@dataclass(frozen=True)
class ZoneConfig:
    dbscan_eps_atr_multiplier: float
    dbscan_min_samples: int
    max_zone_width_atr: float
    merge_overlap_ratio: float


@dataclass(frozen=True)
class TrendlineConfig:
    min_points: int
    max_lines: int
    regression_window: int
    touch_tolerance_atr: float


@dataclass(frozen=True)
class ConfidenceConfig:
    threshold: float
    weights: dict[str, float]


@dataclass(frozen=True)
class BreakoutConfig:
    lookahead_candles: int
    breakout_buffer_atr: float
    low_volume_ratio: float
    reversal_volume_ratio: float
    rolling_volume_window: int
    trendline_tolerance_atr: float


@dataclass(frozen=True)
class BacktestConfig:
    max_holding_bars: int
    target_atr: float
    stop_atr: float


@dataclass(frozen=True)
class VisualizationConfig:
    title: str
    output_html: Path
    output_signals_csv: Path
    output_zones_csv: Path
    max_candles: int


@dataclass(frozen=True)
class LoggingConfig:
    level: str
    file: Path


@dataclass(frozen=True)
class Settings:
    project_root: Path
    data: DataConfig
    resampling: ResamplingConfig
    swing: SwingConfig
    zones: ZoneConfig
    trendlines: TrendlineConfig
    confidence: ConfidenceConfig
    breakout: BreakoutConfig
    backtest: BacktestConfig
    visualization: VisualizationConfig
    logging: LoggingConfig

    def resolve(self, value: Path) -> Path:
        return value if value.is_absolute() else self.project_root / value


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Configuration file {path} must contain a mapping.")
    return data


def load_settings(config_path: str | Path = "config/config.yaml") -> Settings:
    config_file = Path(config_path)
    absolute_config = config_file if config_file.is_absolute() else Path.cwd() / config_file
    if not absolute_config.exists():
        absolute_config = Path(__file__).resolve().parents[1] / config_file
    project_root = absolute_config.resolve().parents[1]
    raw = _load_yaml(absolute_config)

    return Settings(
        project_root=project_root,
        data=DataConfig(
            input_path=Path(raw["data"]["input_path"]),
            datetime_column=raw["data"]["datetime_column"],
            timezone=raw["data"]["timezone"],
            required_columns=list(raw["data"]["required_columns"]),
            duplicate_policy=raw["data"].get("duplicate_policy", "last"),
        ),
        resampling=ResamplingConfig(
            base_timeframe=raw["resampling"]["base_timeframe"],
            timeframes=[TimeframeConfig(**item) for item in raw["resampling"]["timeframes"]],
        ),
        swing=SwingConfig(**raw["swing"]),
        zones=ZoneConfig(**raw["zones"]),
        trendlines=TrendlineConfig(**raw["trendlines"]),
        confidence=ConfidenceConfig(**raw["confidence"]),
        breakout=BreakoutConfig(**raw["breakout"]),
        backtest=BacktestConfig(**raw["backtest"]),
        visualization=VisualizationConfig(
            title=raw["visualization"]["title"],
            output_html=Path(raw["visualization"]["output_html"]),
            output_signals_csv=Path(raw["visualization"]["output_signals_csv"]),
            output_zones_csv=Path(raw["visualization"]["output_zones_csv"]),
            max_candles=int(raw["visualization"].get("max_candles", 2500)),
        ),
        logging=LoggingConfig(level=raw["logging"]["level"], file=Path(raw["logging"]["file"])),
    )
