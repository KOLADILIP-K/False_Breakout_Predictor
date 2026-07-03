from __future__ import annotations

import pandas as pd

from config.settings import BacktestConfig
from src.core.metrics import calculate_performance
from src.models.signal import Signal, SignalDirection


class Backtester:
    def __init__(self, config: BacktestConfig) -> None:
        self.config = config

    def run(self, data: pd.DataFrame, signals: list[Signal]) -> tuple[pd.DataFrame, dict[str, object]]:
        rows: list[dict[str, object]] = []
        for signal in signals:
            if signal.timestamp not in data.index:
                continue
            start = data.index.get_loc(signal.timestamp)
            if isinstance(start, slice):
                start = start.start
            entry_row = data.iloc[start]
            atr = max(float(entry_row.get("atr", entry_row["high"] - entry_row["low"])), 1e-9)
            future = data.iloc[start + 1 : start + 1 + self.config.max_holding_bars]
            if future.empty:
                continue
            multiplier = -1.0 if signal.direction is SignalDirection.SHORT else 1.0
            entry = signal.price
            target = entry + multiplier * atr * self.config.target_atr
            stop = entry - multiplier * atr * self.config.stop_atr
            outcome = "timeout"
            exit_price = float(future.iloc[-1]["close"])
            holding = len(future)
            favorable: list[float] = []
            adverse: list[float] = []
            for offset, (_, row) in enumerate(future.iterrows(), start=1):
                high = float(row["high"])
                low = float(row["low"])
                if signal.direction is SignalDirection.SHORT:
                    favorable.append(entry - low)
                    adverse.append(high - entry)
                    if low <= target:
                        outcome, exit_price, holding = "win", target, offset
                        break
                    if high >= stop:
                        outcome, exit_price, holding = "loss", stop, offset
                        break
                else:
                    favorable.append(high - entry)
                    adverse.append(entry - low)
                    if high >= target:
                        outcome, exit_price, holding = "win", target, offset
                        break
                    if low <= stop:
                        outcome, exit_price, holding = "loss", stop, offset
                        break
            rows.append({
                **signal.to_dict(),
                "entry": entry,
                "exit": exit_price,
                "outcome": outcome,
                "holding_bars": holding,
                "mae": max(adverse) if adverse else 0.0,
                "mfe": max(favorable) if favorable else 0.0,
            })
        trades = pd.DataFrame(rows)
        return trades, calculate_performance(trades)
