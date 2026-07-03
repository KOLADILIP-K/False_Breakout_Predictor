from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ZoneType(str, Enum):
    SUPPORT = "support"
    RESISTANCE = "resistance"


@dataclass(slots=True)
class Zone:
    id: str
    zone_type: ZoneType
    lower: float
    upper: float
    midpoint: float
    timeframe: str
    touch_count: int
    first_touch: datetime
    last_touch: datetime
    relative_volume: float = 1.0
    reversal_strength: float = 0.0
    trend_strength: float = 0.0
    confidence: float = 0.0
    metadata: dict[str, float | str | int] = field(default_factory=dict)

    @property
    def width(self) -> float:
        return max(self.upper - self.lower, 0.0)

    def contains(self, price: float) -> bool:
        return self.lower <= price <= self.upper

    def distance_to(self, price: float) -> float:
        if self.contains(price):
            return 0.0
        return min(abs(price - self.lower), abs(price - self.upper))

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "zone_type": self.zone_type.value,
            "lower": self.lower,
            "upper": self.upper,
            "midpoint": self.midpoint,
            "timeframe": self.timeframe,
            "touch_count": self.touch_count,
            "first_touch": self.first_touch,
            "last_touch": self.last_touch,
            "relative_volume": self.relative_volume,
            "reversal_strength": self.reversal_strength,
            "trend_strength": self.trend_strength,
            "confidence": self.confidence,
            **self.metadata,
        }
