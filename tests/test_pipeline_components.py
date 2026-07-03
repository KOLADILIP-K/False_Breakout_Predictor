from __future__ import annotations

from datetime import datetime, timezone

from config.settings import ConfidenceConfig
from src.core.confidence import ConfidenceScorer
from src.models.zone import Zone, ZoneType


def test_confidence_score_is_bounded() -> None:
    config = ConfidenceConfig(
        threshold=60,
        weights={"touch_count": 1, "relative_volume": 1, "timeframe": 1, "trend_strength": 1, "reversal_strength": 1, "recency": 1, "zone_width": 1},
    )
    zone = Zone(
        id="z1",
        zone_type=ZoneType.RESISTANCE,
        lower=100,
        upper=102,
        midpoint=101,
        timeframe="1h",
        touch_count=5,
        first_touch=datetime(2026, 1, 1, tzinfo=timezone.utc),
        last_touch=datetime(2026, 1, 2, tzinfo=timezone.utc),
        relative_volume=1.2,
        reversal_strength=0.5,
        trend_strength=0.4,
    )
    score = ConfidenceScorer(config, {"1h": 1.0}).score_zone(zone, datetime(2026, 1, 2, tzinfo=timezone.utc), 3.0)
    assert 0 <= score <= 100
