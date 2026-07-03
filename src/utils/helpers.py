from __future__ import annotations

import math
from collections.abc import Iterable


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0 or math.isnan(denominator):
        return default
    return numerator / denominator


def normalize(value: float, low: float, high: float) -> float:
    if high <= low:
        return 0.0
    return clamp((value - low) / (high - low))


def weighted_average(values: dict[str, float], weights: dict[str, float]) -> float:
    total_weight = sum(max(weight, 0.0) for weight in weights.values())
    if total_weight == 0:
        return 0.0
    return sum(values.get(key, 0.0) * max(weight, 0.0) for key, weight in weights.items()) / total_weight


def mean_or_zero(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0
