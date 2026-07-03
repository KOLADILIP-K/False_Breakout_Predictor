from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SignalType(str, Enum):
    FALSE_BREAKOUT = "false_breakout"
    FALSE_BREAKDOWN = "false_breakdown"


class SignalDirection(str, Enum):
    SHORT = "short"
    LONG = "long"


@dataclass(slots=True)
class Signal:
    id: str
    signal_type: SignalType
    direction: SignalDirection
    timestamp: datetime
    price: float
    zone_id: str
    zone_confidence: float
    volume_ratio: float
    return_bars: int
    trendline_confirmation: bool
    confidence: float
    timeframe: str
    metadata: dict[str, float | str | int | bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "signal_type": self.signal_type.value,
            "direction": self.direction.value,
            "timestamp": self.timestamp,
            "price": self.price,
            "zone_id": self.zone_id,
            "zone_confidence": self.zone_confidence,
            "volume_ratio": self.volume_ratio,
            "return_bars": self.return_bars,
            "trendline_confirmation": self.trendline_confirmation,
            "confidence": self.confidence,
            "timeframe": self.timeframe,
            **self.metadata,
        }
