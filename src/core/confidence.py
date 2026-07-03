from __future__ import annotations

from datetime import datetime

from config.settings import ConfidenceConfig
from src.models.zone import Zone
from src.utils.helpers import clamp, normalize, safe_divide, weighted_average


class ConfidenceScorer:
    def __init__(self, config: ConfidenceConfig, timeframe_weights: dict[str, float]) -> None:
        self.config = config
        self.timeframe_weights = timeframe_weights

    def score_zone(self, zone: Zone, latest_time: datetime, average_atr: float) -> float:
        age_seconds = max((latest_time - zone.last_touch).total_seconds(), 0.0)
        recency = 1.0 / (1.0 + age_seconds / 86_400.0)
        components = {
            "touch_count": normalize(zone.touch_count, 1.0, 8.0),
            "relative_volume": normalize(zone.relative_volume, 0.5, 2.0),
            "timeframe": clamp(self.timeframe_weights.get(zone.timeframe, 0.5)),
            "trend_strength": clamp(zone.trend_strength),
            "reversal_strength": clamp(zone.reversal_strength),
            "recency": clamp(recency),
            "zone_width": 1.0 - clamp(safe_divide(zone.width, average_atr * 3.0, 1.0)),
        }
        return round(weighted_average(components, self.config.weights) * 100.0, 2)
