from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.settings import VisualizationConfig
from src.models.signal import Signal, SignalType
from src.models.trendline import Trendline
from src.models.zone import Zone, ZoneType
from src.visualization.charts import candlestick_trace
from src.visualization.plotting import confidence_color


class DashboardBuilder:
    def __init__(self, config: VisualizationConfig, project_root: Path) -> None:
        self.config = config
        self.project_root = project_root

    def build(self, data: pd.DataFrame, zones: list[Zone], trendlines: list[Trendline], signals: list[Signal]) -> go.Figure:
        frame = data.tail(self.config.max_candles)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.75, 0.25])
        fig.add_trace(candlestick_trace(frame), row=1, col=1)
        fig.add_trace(go.Bar(x=frame.index, y=frame["volume"], name="Volume", marker_color="rgba(100,116,139,0.45)"), row=2, col=1)
        self._add_zones(fig, frame, zones)
        self._add_trendlines(fig, frame, trendlines)
        self._add_signals(fig, signals)
        fig.update_layout(
            title=self.config.title,
            template="plotly_white",
            hovermode="x unified",
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=860,
        )
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        return fig

    def export(self, figure: go.Figure) -> Path:
        output_path = self.project_root / self.config.output_html
        output_path.parent.mkdir(parents=True, exist_ok=True)
        figure.write_html(output_path, include_plotlyjs="cdn")
        return output_path

    def _add_zones(self, fig: go.Figure, data: pd.DataFrame, zones: list[Zone]) -> None:
        if data.empty:
            return
        x0, x1 = data.index.min(), data.index.max()
        for zone in zones:
            color = confidence_color(zone.confidence)
            fig.add_shape(type="rect", x0=x0, x1=x1, y0=zone.lower, y1=zone.upper, fillcolor=color, line_width=0, layer="below", row=1, col=1)
            fig.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[zone.midpoint, zone.midpoint],
                    mode="lines",
                    line=dict(width=1, dash="dot"),
                    name=f"{zone.zone_type.value} {zone.timeframe} {zone.confidence:.1f}",
                    hovertemplate="Zone %{y:.2f}<extra></extra>",
                ),
                row=1,
                col=1,
            )

    def _add_trendlines(self, fig: go.Figure, data: pd.DataFrame, trendlines: list[Trendline]) -> None:
        if data.empty:
            return
        positions = list(range(len(data)))
        for line in trendlines:
            y = [line.value_at_position(position) for position in positions]
            fig.add_trace(go.Scatter(x=data.index, y=y, mode="lines", name=f"{line.kind} TL {line.confidence:.1f}", line=dict(width=1.5)), row=1, col=1)

    def _add_signals(self, fig: go.Figure, signals: list[Signal]) -> None:
        breakouts = [signal for signal in signals if signal.signal_type is SignalType.FALSE_BREAKOUT]
        breakdowns = [signal for signal in signals if signal.signal_type is SignalType.FALSE_BREAKDOWN]
        if breakouts:
            fig.add_trace(go.Scatter(x=[s.timestamp for s in breakouts], y=[s.price for s in breakouts], mode="markers", name="False Breakout", marker=dict(symbol="triangle-down", size=12, color="#dc2626"), text=[f"Confidence {s.confidence}" for s in breakouts]), row=1, col=1)
        if breakdowns:
            fig.add_trace(go.Scatter(x=[s.timestamp for s in breakdowns], y=[s.price for s in breakdowns], mode="markers", name="False Breakdown", marker=dict(symbol="triangle-up", size=12, color="#16a34a"), text=[f"Confidence {s.confidence}" for s in breakdowns]), row=1, col=1)
