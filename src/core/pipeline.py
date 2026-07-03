from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from config.settings import Settings
from src.core.backtester import Backtester
from src.core.breakout_detector import FalseBreakoutDetector
from src.core.clustering import SupportResistanceClusterer
from src.core.confidence import ConfidenceScorer
from src.core.data_loader import MarketDataLoader
from src.core.resampler import MarketDataResampler
from src.core.signal_validator import SignalValidator
from src.core.swing_detector import SwingDetector
from src.core.trendline_detector import TrendlineDetector
from src.models.signal import Signal
from src.models.trendline import Trendline
from src.models.zone import Zone
from src.visualization.dashboard import DashboardBuilder

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineResult:
    base_data: pd.DataFrame
    timeframe_data: dict[str, pd.DataFrame]
    zones: list[Zone]
    trendlines: list[Trendline]
    signals: list[Signal]
    trades: pd.DataFrame
    metrics: dict[str, object]
    dashboard_path: Path


class FalseBreakoutPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        timeframe_weights = {item.name: item.weight for item in settings.resampling.timeframes}
        self.loader = MarketDataLoader(settings.data, settings.project_root)
        self.resampler = MarketDataResampler()
        self.swing_detector = SwingDetector(settings.swing)
        self.clusterer = SupportResistanceClusterer(settings.zones)
        self.confidence = ConfidenceScorer(settings.confidence, timeframe_weights)
        self.trendlines = TrendlineDetector(settings.trendlines)
        self.breakouts = FalseBreakoutDetector(settings.breakout, settings.confidence)
        self.validator = SignalValidator(settings.confidence)
        self.backtester = Backtester(settings.backtest)
        self.dashboard = DashboardBuilder(settings.visualization, settings.project_root)

    def run(self) -> PipelineResult:
        base = self.loader.load()
        timeframe_rules = {item.name: item.rule for item in self.settings.resampling.timeframes}
        frames = self.resampler.multi_timeframe(base, timeframe_rules)
        zones: list[Zone] = []
        trendlines: list[Trendline] = []
        signals: list[Signal] = []
        for timeframe, frame in frames.items():
            LOGGER.info("Processing timeframe %s", timeframe)
            enriched = self.swing_detector.detect(frame)
            frames[timeframe] = enriched
            tf_zones = self.clusterer.detect_zones(enriched, timeframe)
            latest_time = enriched.index.max().to_pydatetime()
            average_atr = float(enriched["atr"].mean())
            for zone in tf_zones:
                zone.confidence = self.confidence.score_zone(zone, latest_time, average_atr)
            tf_trendlines = self.trendlines.detect(enriched, timeframe)
            tf_signals = self.validator.filter_valid(self.breakouts.detect(enriched, tf_zones, tf_trendlines, timeframe))
            zones.extend(tf_zones)
            trendlines.extend(tf_trendlines)
            signals.extend(tf_signals)
        base_enriched = self.swing_detector.detect(base)
        trades, metrics = self.backtester.run(base_enriched, signals)
        dashboard_path = self._export(base_enriched, zones, trendlines, signals, trades, metrics)
        return PipelineResult(base_enriched, frames, zones, trendlines, signals, trades, metrics, dashboard_path)

    def _export(self, base: pd.DataFrame, zones: list[Zone], trendlines: list[Trendline], signals: list[Signal], trades: pd.DataFrame, metrics: dict[str, object]) -> Path:
        zones_path = self.settings.project_root / self.settings.visualization.output_zones_csv
        signals_path = self.settings.project_root / self.settings.visualization.output_signals_csv
        metrics_path = self.settings.project_root / "output" / "metrics.json"
        zones_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([zone.to_dict() for zone in zones]).to_csv(zones_path, index=False)
        pd.DataFrame([signal.to_dict() for signal in signals]).to_csv(signals_path, index=False)
        trades.to_csv(self.settings.project_root / "output" / "trades.csv", index=False)
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        figure = self.dashboard.build(base, zones, trendlines, signals)
        dashboard_path = self.dashboard.export(figure)
        LOGGER.info("Exported %d zones, %d signals, and dashboard to %s", len(zones), len(signals), dashboard_path)
        return dashboard_path
