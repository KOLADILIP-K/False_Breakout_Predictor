from __future__ import annotations

import uuid

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

from config.settings import ZoneConfig
from src.models.zone import Zone, ZoneType
from src.utils.helpers import safe_divide


class SupportResistanceClusterer:
    def __init__(self, config: ZoneConfig) -> None:
        self.config = config

    def detect_zones(self, data: pd.DataFrame, timeframe: str) -> list[Zone]:
        zones: list[Zone] = []
        zones.extend(self._cluster_points(data, timeframe, ZoneType.RESISTANCE, "swing_high", "high"))
        zones.extend(self._cluster_points(data, timeframe, ZoneType.SUPPORT, "swing_low", "low"))
        return sorted(zones, key=lambda zone: (zone.timeframe, zone.midpoint))

    def _cluster_points(self, data: pd.DataFrame, timeframe: str, zone_type: ZoneType, flag: str, price_col: str) -> list[Zone]:
        points = data[data[flag]].copy()
        if points.empty:
            return []
        average_atr = float(points["atr"].mean()) if "atr" in points else float((data["high"] - data["low"]).mean())
        eps = max(average_atr * self.config.dbscan_eps_atr_multiplier, 1e-9)
        labels = DBSCAN(eps=eps, min_samples=self.config.dbscan_min_samples).fit_predict(points[[price_col]].to_numpy())
        points["cluster"] = labels
        zones: list[Zone] = []
        for label in sorted(set(labels)):
            if label == -1:
                continue
            cluster = points[points["cluster"] == label]
            prices = cluster[price_col]
            width = float(prices.max() - prices.min())
            if average_atr > 0 and width > average_atr * self.config.max_zone_width_atr:
                continue
            zone = Zone(
                id=f"{timeframe}-{zone_type.value}-{uuid.uuid4().hex[:8]}",
                zone_type=zone_type,
                lower=float(prices.min()),
                upper=float(prices.max()),
                midpoint=float(prices.mean()),
                timeframe=timeframe,
                touch_count=int(len(cluster)),
                first_touch=cluster.index.min().to_pydatetime(),
                last_touch=cluster.index.max().to_pydatetime(),
                relative_volume=float(safe_divide(cluster["volume"].mean(), data["volume"].rolling(20, min_periods=1).mean().mean(), 1.0)),
                reversal_strength=self._reversal_strength(data, cluster.index, zone_type),
                trend_strength=self._trend_strength(data),
                metadata={"average_atr": average_atr},
            )
            zones.append(zone)
        return zones

    def _reversal_strength(self, data: pd.DataFrame, timestamps: pd.Index, zone_type: ZoneType) -> float:
        strengths: list[float] = []
        for timestamp in timestamps:
            position = data.index.get_loc(timestamp)
            if isinstance(position, slice) or position == 0 or position >= len(data) - 1:
                continue
            current = data.iloc[position]
            following = data.iloc[position + 1]
            atr = max(float(current.get("atr", current["high"] - current["low"])), 1e-9)
            if zone_type is ZoneType.RESISTANCE:
                strengths.append(max(0.0, current["high"] - following["close"]) / atr)
            else:
                strengths.append(max(0.0, following["close"] - current["low"]) / atr)
        return float(min(np.mean(strengths), 1.0)) if strengths else 0.0

    def _trend_strength(self, data: pd.DataFrame) -> float:
        if len(data) < 3:
            return 0.0
        x = np.arange(len(data), dtype=float)
        y = data["close"].to_numpy(dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        fitted = slope * x + intercept
        total = np.sum((y - y.mean()) ** 2)
        residual = np.sum((y - fitted) ** 2)
        return float(max(0.0, min(1.0, 1.0 - residual / total))) if total else 0.0
