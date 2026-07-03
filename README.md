# False Breakout Detection

A production-quality Python 3.11 project for detecting support, resistance, trendlines, false breakouts, and false breakdowns from historical OHLCV market data.

## Problem Statement

The system consumes one-minute market data with `datetime`, `open`, `high`, `low`, `close`, `volume`, and `oi`. It cleans the data, builds 15-minute and 1-hour views, detects swing points, clusters support and resistance zones, scores confidence, confirms trendlines, detects failed moves beyond high-confidence levels, backtests the resulting signals, and exports CSV plus an interactive Plotly HTML dashboard.

## Architecture

- `config/`: YAML-driven configuration and typed settings classes.
- `src/core/`: data loading, resampling, swing detection, DBSCAN clustering, trendlines, confidence scoring, signal detection, validation, backtesting, and orchestration.
- `src/indicators/`: ATR, moving averages, volatility, and relative volume.
- `src/models/`: dataclasses for zones, trendlines, and signals.
- `src/visualization/`: Plotly dashboard and chart helpers.
- `tests/`: unit tests for cleaning, indicators, confidence, and signal logic.

## Algorithms

### Swing Detection

For each candle `i`, the system compares the candle high and low with a symmetric lookback window. A swing is accepted only when its prominence exceeds `threshold_i = ATR_i * atr_multiplier`.

### Support and Resistance Zones

Swing highs form resistance candidates and swing lows form support candidates. Each price set is clustered using DBSCAN with `eps = mean(ATR) * dbscan_eps_atr_multiplier`.

### Trendlines

The latest swing points are fit with ordinary least squares: `price = slope * bar_position + intercept`. Trendline confidence uses `R^2` and the number of touches.

### Confidence Score

Every zone receives a normalized 0-100 score: `score = 100 * sum(component_i * weight_i) / sum(weight_i)`. Components are touch count, relative volume, timeframe weight, trend strength, reversal strength, recency, and zone width.

### False Breakout Logic

A signal is emitted when price closes beyond a high-confidence zone, volume behavior indicates weakness or reversal, price returns inside the zone within N candles, and trendline confirmation agrees.

## How to Run

1. `cd FalseBreakoutDetection`
2. `python -m venv .venv`
3. `.venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. `python main.py`

Outputs are written to `output/`: `dashboard.html`, `signals.csv`, `zones.csv`, `trades.csv`, `metrics.json`, and `pipeline.log`.

## Tests

Run `pytest` from the repository root.

## Dashboard

The dashboard contains candlesticks, support/resistance zones shaded by confidence, trendlines, volume, and markers for false breakouts and false breakdowns. Open `output/dashboard.html` after running the pipeline.

## Design Decisions

- ATR-adaptive thresholds make the detector robust across volatility regimes.
- DBSCAN avoids requiring a fixed number of support/resistance zones.
- Configuration is externalized so confidence weights and detection thresholds are auditable.
- Dataclasses keep domain objects explicit and easy to serialize.
- The backtester is deterministic and transparent for assignment review.

## Screenshots

Run `python main.py` and open `output/dashboard.html` to capture dashboard screenshots for submission.

## Future Improvements

- Add walk-forward parameter optimization.
- Add out-of-sample validation across multiple instruments.
- Include order book features if future data sources permit them.
- Add dashboard controls for timeframe and confidence filtering.
- Persist results in Parquet for faster iterative research.

## References

- J. Welles Wilder, New Concepts in Technical Trading Systems, ATR.
- Ester et al., A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise, DBSCAN.
- Plotly Python documentation for interactive financial charts.
- scikit-learn DBSCAN documentation.
