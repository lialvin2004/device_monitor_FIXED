"""
chart_widget.py
Live matplotlib line chart embedded in a Tkinter Frame via FigureCanvasTkAgg.
"""

import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from sensor import Sensor
from theme import Palette

_COLORS_DARK  = ["#63b3ed", "#68d391", "#f6ad55"]
_COLORS_LIGHT = ["#2b6cb0", "#276749", "#c05621"]


class ChartWidget(tk.Frame):
    def __init__(self, parent: tk.Widget, palette: Palette) -> None:
        super().__init__(parent)
        self._palette = palette
        self._build_ui(palette)

    def _build_ui(self, p: Palette) -> None:
        self._fig = Figure(figsize=(6, 3), dpi=96, facecolor=p.chart_bg)
        self._ax = self._fig.add_subplot(111)
        self._style_axes(p)

        self._line, = self._ax.plot([], [], color=_COLORS_DARK[0], linewidth=2)
        self._thresh_line = self._ax.axhline(
            y=0, color="#fc8181", linestyle="--", linewidth=1, alpha=0.8)

        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas.draw()

    def _style_axes(self, p: Palette) -> None:
        ax = self._ax
        ax.set_facecolor(p.chart_bg)
        ax.tick_params(colors=p.fg_dim, labelsize=8)
        ax.set_xlabel("Time (s)", fontsize=8, color=p.fg_dim)
        for spine in ax.spines.values():
            spine.set_edgecolor(p.border)
        ax.grid(True, color=p.chart_grid, linewidth=0.5)
        self._fig.tight_layout(pad=1.2)

    def update_chart(self, sensor: Sensor, color_index: int = 0) -> None:
        xs = sensor.history_timestamps
        ys = sensor.history_values

        p = self._palette
        colors = _COLORS_DARK if p.chart_bg != "#ffffff" else _COLORS_LIGHT
        self._line.set_data(xs, ys)
        self._line.set_color(colors[color_index % len(colors)])
        self._thresh_line.set_ydata([sensor.threshold, sensor.threshold])

        self._ax.set_title(f"{sensor.name}  ({sensor.unit})",
                           fontsize=10, color=p.fg_label, pad=6)

        if xs:
            self._ax.set_xlim(max(0, xs[-1] - 30), xs[-1] + 1)
        else:
            self._ax.set_xlim(0, 30)

        if ys:
            lo, hi = min(ys), max(ys)
            pad = max((hi - lo) * 0.2, 2.0)
            self._ax.set_ylim(lo - pad, hi + pad)
        else:
            # No data — centre around threshold so the dashed line is visible
            self._ax.set_ylim(sensor.threshold - 20, sensor.threshold + 20)

        self._canvas.draw_idle()

    def clear(self, sensor: Sensor) -> None:
        """Wipe the chart line and recentre around the current threshold."""
        self._line.set_data([], [])
        self._thresh_line.set_ydata([sensor.threshold, sensor.threshold])
        self._ax.set_xlim(0, 30)
        self._ax.set_ylim(sensor.threshold - 20, sensor.threshold + 20)
        self._ax.set_title(f"{sensor.name}  ({sensor.unit})",
                           fontsize=10, color=self._palette.fg_label, pad=6)
        self._canvas.draw_idle()

    def apply_palette(self, palette: Palette) -> None:
        self._palette = palette
        p = palette
        self._fig.set_facecolor(p.chart_bg)
        self._ax.set_facecolor(p.chart_bg)
        self._ax.tick_params(colors=p.fg_dim)
        for spine in self._ax.spines.values():
            spine.set_edgecolor(p.border)
        self._ax.grid(True, color=p.chart_grid, linewidth=0.5)
        self._ax.xaxis.label.set_color(p.fg_dim)
        self._ax.title.set_color(p.fg_label)
        self._canvas.draw_idle()