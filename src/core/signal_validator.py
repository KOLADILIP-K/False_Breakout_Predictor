from __future__ import annotations

from config.settings import ConfidenceConfig
from src.models.signal import Signal


class SignalValidator:
    def __init__(self, config: ConfidenceConfig) -> None:
        self.config = config

    def validate(self, signal: Signal) -> bool:
        return (
            signal.zone_confidence >= self.config.threshold
            and signal.confidence >= self.config.threshold
            and signal.return_bars > 0
            and signal.trendline_confirmation
        )

    def filter_valid(self, signals: list[Signal]) -> list[Signal]:
        return [signal for signal in signals if self.validate(signal)]
