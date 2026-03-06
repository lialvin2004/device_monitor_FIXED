"""
controls_panel.py
All user controls in one Tkinter Frame. Communicates via plain Python callbacks.
Contains zero business logic — only displays controls and invokes callbacks.
"""

import tkinter as tk
from typing import Callable, List

from sensor import Sensor
from theme import Palette


class ControlsPanel(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        sensors: List[Sensor],
        palette: Palette,
        on_start_stop: Callable,
        on_sensor_changed: Callable[[int], None],
        on_threshold_changed: Callable[[float], None],
        on_reset: Callable,
        on_export: Callable,
        on_theme_toggle: Callable,
    ) -> None:
        super().__init__(parent)
        self._sensors = sensors
        self._palette = palette
        self._on_start_stop = on_start_stop
        self._on_sensor_changed = on_sensor_changed
        self._on_threshold_changed = on_threshold_changed
        self._on_reset = on_reset
        self._on_export = on_export
        self._on_theme_toggle = on_theme_toggle
        self._build_ui(palette)
        self._apply_palette(palette)

    def _section(self, text: str) -> tk.Label:
        return tk.Label(self, text=text, font=("Courier New", 8, "bold"), anchor="w")

    def _btn(self, text: str, cmd: Callable) -> tk.Button:
        return tk.Button(self, text=text, font=("Courier New", 11),
                         relief=tk.FLAT, cursor="hand2", command=cmd)

    def _build_ui(self, p: Palette) -> None:
        pad = {"padx": 10, "pady": 4}

        self._sim_lbl = self._section("SIMULATION")
        self._sim_lbl.pack(fill=tk.X, **pad)

        self._start_stop_btn = self._btn("▶  Start", self._on_start_stop)
        self._start_stop_btn.pack(fill=tk.X, padx=10, pady=(0, 4))

        self._reset_btn = self._btn("↺  Reset", self._on_reset)
        self._reset_btn.pack(fill=tk.X, padx=10, pady=(0, 12))

        self._chart_lbl = self._section("CHART SENSOR")
        self._chart_lbl.pack(fill=tk.X, **pad)

        self._sensor_var = tk.StringVar(value=self._sensors[0].name)
        self._sensor_menu = tk.OptionMenu(
            self, self._sensor_var, *[s.name for s in self._sensors],
            command=self._on_combo_change,
        )
        self._sensor_menu.config(font=("Courier New", 10), relief=tk.FLAT,
                                 cursor="hand2", anchor="w")
        self._sensor_menu["menu"].config(font=("Courier New", 10))
        self._sensor_menu.pack(fill=tk.X, padx=10, pady=(0, 12))

        self._thresh_lbl = self._section("WARNING THRESHOLD")
        self._thresh_lbl.pack(fill=tk.X, **pad)

        self._thresh_val_lbl = tk.Label(self, font=("Courier New", 10), anchor="center")
        self._thresh_val_lbl.pack(fill=tk.X, padx=10)

        self._slider_var = tk.DoubleVar()
        self._slider = tk.Scale(self, variable=self._slider_var,
                                orient=tk.HORIZONTAL, showvalue=False,
                                command=self._on_scale_change)
        self._slider.pack(fill=tk.X, padx=10, pady=(0, 12))

        self._tools_lbl = self._section("TOOLS")
        self._tools_lbl.pack(fill=tk.X, **pad)

        self._export_btn = self._btn("⬇  Export CSV", self._on_export)
        self._export_btn.pack(fill=tk.X, padx=10, pady=(0, 4))

        self._theme_btn = self._btn("◑  Toggle Theme", self._on_theme_toggle)
        self._theme_btn.pack(fill=tk.X, padx=10, pady=(0, 4))

        self._refresh_slider(0)

    def set_running(self, running: bool) -> None:
        p = self._palette
        if running:
            self._start_stop_btn.config(text="⏸  Stop", fg=p.accent_red,
                                        activeforeground=p.accent_red)
        else:
            self._start_stop_btn.config(text="▶  Start", fg=p.accent_green,
                                        activeforeground=p.accent_green)

    def apply_palette(self, palette: Palette) -> None:
        self._palette = palette
        self._apply_palette(palette)

    def _on_combo_change(self, value: str) -> None:
        idx = next(i for i, s in enumerate(self._sensors) if s.name == value)
        self._refresh_slider(idx)
        self._on_sensor_changed(idx)

    def _on_scale_change(self, _=None) -> None:
        idx = next(i for i, s in enumerate(self._sensors)
                   if s.name == self._sensor_var.get())
        sensor = self._sensors[idx]
        scaled = sensor.min_value + (self._slider_var.get() / 100.0) * \
                 (sensor.max_value - sensor.min_value)
        self._thresh_val_lbl.config(text=f"{scaled:.1f} {sensor.unit}")
        self._on_threshold_changed(scaled)

    def _refresh_slider(self, idx: int) -> None:
        sensor = self._sensors[idx]
        pos = int((sensor.threshold - sensor.min_value) /
                  (sensor.max_value - sensor.min_value) * 100)
        self._slider.config(from_=0, to=100)
        self._slider_var.set(pos)
        self._thresh_val_lbl.config(text=f"{sensor.threshold:.1f} {sensor.unit}")

    def _apply_palette(self, p: Palette) -> None:
        self.config(bg=p.bg)
        for w in (self._sim_lbl, self._chart_lbl, self._thresh_lbl,
                  self._tools_lbl, self._thresh_val_lbl):
            w.config(bg=p.bg, fg=p.fg_dim)
        for btn in (self._reset_btn, self._export_btn, self._theme_btn):
            btn.config(bg=p.btn_bg, fg=p.btn_fg,
                       activebackground=p.btn_active, activeforeground=p.btn_fg)
        self._start_stop_btn.config(bg=p.btn_bg, activebackground=p.btn_active)
        self._sensor_menu.config(bg=p.btn_bg, fg=p.btn_fg,
                                 activebackground=p.btn_active, activeforeground=p.btn_fg)
        self._sensor_menu["menu"].config(bg=p.btn_bg, fg=p.btn_fg)
        self._slider.config(bg=p.bg, fg=p.accent, troughcolor=p.border,
                            activebackground=p.accent, highlightbackground=p.bg)
