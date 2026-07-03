from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Trendline:
    id: str
    kind: str
    timeframe: str
    slope: float
    intercept: float
    r_squared: float
    touches: int
    start_time: datetime
    end_time: datetime
    confidence: float

    def value_at_position(self, position: int | float) -> float:
        return self.slope * float(position) + self.intercept

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "kind": self.kind,
            "timeframe": self.timeframe,
            "slope": self.slope,
            "intercept": self.intercept,
            "r_squared": self.r_squared,
            "touches": self.touches,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "confidence": self.confidence,
        }
