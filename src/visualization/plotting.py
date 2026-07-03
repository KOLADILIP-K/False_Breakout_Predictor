from __future__ import annotations


def confidence_color(score: float) -> str:
    if score >= 80:
        return "rgba(16, 185, 129, 0.35)"
    if score >= 65:
        return "rgba(245, 158, 11, 0.35)"
    return "rgba(239, 68, 68, 0.25)"
