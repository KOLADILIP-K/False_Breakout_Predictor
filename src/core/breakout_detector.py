from __future__ import annotations

import uuid

import pandas as pd

from config.settings import BreakoutConfig, ConfidenceConfig
from src.models.signal import Signal, SignalDirection, SignalType
from src.models.trendline import Trendline
from src.models.zone import Zone, ZoneType


class FalseBreakoutDetector:
    def __init__(self, config: BreakoutConfig, confidence_config: ConfidenceConfig) -> None:
        self.config = config
        self.confidence_config = confidence_config

    def detect(self, data: pd.DataFrame, zones: list[Zone], trendlines: list[Trendline], timeframe: str) -> list[Signal]:
        frame = data.copy()
        frame["rolling_volume"] = frame["volume"].rolling(self.config.rolling_volume_window, min_periods=1).mean()
        signals: list[Signal] = []
        for zone in zones:
            if zone.confidence < self.confidence_config.threshold:
                continue
            signals.extend(self._detect_for_zone(frame, zone, trendlines, timeframe))
        return signals

    def _detect_for_zone(self, data: pd.DataFrame, zone: Zone, trendlines: list[Trendline], timeframe: str) -> list[Signal]:
        signals: list[Signal] = []
        for position in range(1, len(data) - self.config.lookahead_candles):
            row = data.iloc[position]
            atr = max(float(row.get("atr", row["high"] - row["low"])), 1e-9)
            buffer = atr * self.config.breakout_buffer_atr
            rolling_volume = max(float(row["rolling_volume"]), 1e-9)
            volume_ratio = float(row["volume"] / rolling_volume)
            if zone.zone_type is ZoneType.RESISTANCE and row["close"] > zone.upper + buffer:
                return_bars = self._returns_inside(data, position, zone)
                if return_bars and self._volume_condition(data, position, volume_ratio):
                    confirmation = self._trendline_agrees(position, row["close"], trendlines, "resistance", atr)
                    signals.append(self._build_signal(zone, row.name, row["close"], volume_ratio, return_bars, confirmation, timeframe, SignalType.FALSE_BREAKOUT, SignalDirection.SHORT))
            if zone.zone_type is ZoneType.SUPPORT and row["close"] < zone.lower - buffer:
                return_bars = self._returns_inside(data, position, zone)
                if return_bars and self._volume_condition(data, position, volume_ratio):
                    confirmation = self._trendline_agrees(position, row["close"], trendlines, "support", atr)
                    signals.append(self._build_signal(zone, row.name, row["close"], volume_ratio, return_bars, confirmation, timeframe, SignalType.FALSE_BREAKDOWN, SignalDirection.LONG))
        return signals

    def _returns_inside(self, data: pd.DataFrame, start: int, zone: Zone) -> int:
        for offset in range(1, self.config.lookahead_candles + 1):
            close = float(data.iloc[start + offset]["close"])
            if zone.contains(close):
                return offset
        return 0

    def _volume_condition(self, data: pd.DataFrame, position: int, breakout_volume_ratio: float) -> bool:
        if breakout_volume_ratio <= self.config.low_volume_ratio:
            return True
        next_row = data.iloc[position + 1]
        rolling = max(float(next_row["rolling_volume"]), 1e-9)
        return float(next_row["volume"] / rolling) >= self.config.reversal_volume_ratio

    def _trendline_agrees(self, position: int, price: float, trendlines: list[Trendline], kind: str, atr: float) -> bool:
        candidates = [line for line in trendlines if line.kind == kind]
        if not candidates:
            return True
        tolerance = atr * self.config.trendline_tolerance_atr
        return any(abs(price - line.value_at_position(position)) <= tolerance or line.confidence >= 60 for line in candidates)

    def _build_signal(self, zone: Zone, timestamp, price: float, volume_ratio: float, return_bars: int, confirmation: bool, timeframe: str, signal_type: SignalType, direction: SignalDirection) -> Signal:
        confidence = min(100.0, zone.confidence * 0.75 + max(0.0, 1.5 - volume_ratio) * 10.0 + (10.0 if confirmation else 0.0))
        return Signal(
            id=f"{timeframe}-{signal_type.value}-{uuid.uuid4().hex[:8]}",
            signal_type=signal_type,
            direction=direction,
            timestamp=timestamp.to_pydatetime() if hasattr(timestamp, "to_pydatetime") else timestamp,
            price=float(price),
            zone_id=zone.id,
            zone_confidence=zone.confidence,
            volume_ratio=round(volume_ratio, 4),
            return_bars=return_bars,
            trendline_confirmation=confirmation,
            confidence=round(confidence, 2),
            timeframe=timeframe,
            metadata={"zone_lower": zone.lower, "zone_upper": zone.upper},
        )
