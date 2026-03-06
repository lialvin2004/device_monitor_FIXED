"""
sensor_card.py
A compact Tkinter Frame for one sensor: name, live value, unit, warning.
"""

import tkinter as tk
from sensor import Sensor
from theme import Palette


class SensorCard(tk.Frame):
    def __init__(self, parent: tk.Widget, sensor: Sensor, palette: Palette) -> None:
        super().__init__(parent)
        self._sensor = sensor
        self._palette = palette
        self._build_ui()
        self._apply_palette(palette)

    def _build_ui(self) -> None:
        self._name_lbl = tk.Label(self, text=self._sensor.name.upper(),
                                  font=("Courier New", 9, "bold"), anchor="w")
        self._name_lbl.grid(row=0, column=0, sticky="w", padx=(12, 4), pady=(10, 0))

        self._value_lbl = tk.Label(self, text="--",
                                   font=("Courier New", 26, "bold"), anchor="e")
        self._value_lbl.grid(row=0, column=1, sticky="e", padx=(4, 12), pady=(10, 0))

        self._unit_lbl = tk.Label(self, text=self._sensor.unit,
                                  font=("Courier New", 10), anchor="w")
        self._unit_lbl.grid(row=1, column=0, sticky="w", padx=(12, 4), pady=(0, 10))

        self._warn_lbl = tk.Label(self, text="",
                                  font=("Courier New", 9, "bold"), anchor="e")
        self._warn_lbl.grid(row=1, column=1, sticky="e", padx=(4, 12), pady=(0, 10))

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def update_sensor(self, sensor: Sensor) -> None:
        p = self._palette
        self._value_lbl.config(text=f"{sensor.current_value:.1f}")
        if sensor.is_above_threshold:
            self._warn_lbl.config(text=f"⚠ >{sensor.threshold:.0f}", fg=p.accent_red)
            self.config(highlightbackground=p.border_warn, highlightthickness=2)
        else:
            self._warn_lbl.config(text="", fg=p.fg_dim)
            self.config(highlightbackground=p.border, highlightthickness=1)

    def apply_palette(self, palette: Palette) -> None:
        self._palette = palette
        self._apply_palette(palette)

    def _apply_palette(self, p: Palette) -> None:
        self.config(bg=p.bg_card, highlightbackground=p.border, highlightthickness=1)
        self._name_lbl.config(bg=p.bg_card, fg=p.fg_dim)
        self._value_lbl.config(bg=p.bg_card, fg=p.accent)
        self._unit_lbl.config(bg=p.bg_card, fg=p.fg_dim)
        self._warn_lbl.config(bg=p.bg_card, fg=p.fg_dim)
