"""
main_window.py
MainWindow: top-level Tk window and MVC controller.

Bridges threading: engine callbacks fire on a worker thread;
root.after(0, fn) marshals every UI update back to the main thread.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List

from exporter import CsvExporter
from sensor import Sensor
from simulation import SimulationEngine
from theme import ThemeManager, Theme
from sensor_card import SensorCard
from chart_widget import ChartWidget
from controls_panel import ControlsPanel


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self._engine = SimulationEngine()
        self._theme_mgr = ThemeManager()
        self._selected_sensor_index: int = 0

        self.title("Device Monitor Dashboard")
        self.minsize(920, 600)
        self.config(bg=self._theme_mgr.palette.bg)

        self._build_ui()
        self._connect_engine()
        self._apply_theme()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        p = self._theme_mgr.palette

        root_frame = tk.Frame(self, bg=p.bg)
        root_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(12, 0))

        left_col = tk.Frame(root_frame, bg=p.bg)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_col = tk.Frame(root_frame, bg=p.bg, width=210)
        right_col.pack(side=tk.RIGHT, fill=tk.Y, padx=(12, 0))
        right_col.pack_propagate(False)

        # Status indicator
        status_row = tk.Frame(left_col, bg=p.bg)
        status_row.pack(fill=tk.X, pady=(0, 8))
        self._status_lbl = tk.Label(status_row, text="● STOPPED",
                                    font=("Courier New", 10, "bold"),
                                    bg=p.bg, fg=p.accent_red)
        self._status_lbl.pack(side=tk.LEFT)

        # Sensor cards
        cards_frame = tk.Frame(left_col, bg=p.bg)
        cards_frame.pack(fill=tk.X, pady=(0, 12))
        self._sensor_cards: List[SensorCard] = []
        for sensor in self._engine.sensors:
            card = SensorCard(cards_frame, sensor, p)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            self._sensor_cards.append(card)

        # Chart
        self._chart = ChartWidget(left_col, p)
        self._chart.pack(fill=tk.BOTH, expand=True)

        # Controls
        self._controls = ControlsPanel(
            right_col,
            sensors=self._engine.sensors,
            palette=p,
            on_start_stop=self._engine.toggle,
            on_sensor_changed=self._on_sensor_selected,
            on_threshold_changed=self._on_threshold_changed,
            on_reset=self._on_reset,
            on_export=self._on_export,
            on_theme_toggle=self._on_theme_toggle,
        )
        self._controls.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self._status_bar = tk.Label(self,
            text="Ready — press Start to begin simulation",
            font=("Courier New", 9), anchor="w", pady=4)
        self._status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=(4, 4))

    def _connect_engine(self) -> None:
        self._engine.on_tick(
            lambda sensors: self.after(0, lambda: self._on_tick(sensors)))
        self._engine.on_status_changed(
            lambda running: self.after(0, lambda: self._on_status_changed(running)))

    # ── Slots ──────────────────────────────────────────────────────────

    def _on_tick(self, sensors: List[Sensor]) -> None:
        for card, sensor in zip(self._sensor_cards, sensors):
            card.update_sensor(sensor)
        self._chart.update_chart(sensors[self._selected_sensor_index],
                                 self._selected_sensor_index)
        parts = [f"{s.name}: {s.current_value:.1f}{s.unit}" for s in sensors]
        self._status_bar.config(text="  |  ".join(parts))

    def _on_status_changed(self, running: bool) -> None:
        p = self._theme_mgr.palette
        if running:
            self._status_lbl.config(text="● RUNNING", fg=p.accent_green)
        else:
            self._status_lbl.config(text="● STOPPED", fg=p.accent_red)
        self._controls.set_running(running)

    def _on_sensor_selected(self, index: int) -> None:
        self._selected_sensor_index = index
        sensor = self._engine.sensors[index]
        # Always redraw immediately — works while stopped too
        if sensor.history:
            self._chart.update_chart(sensor, index)
        else:
            self._chart.clear(sensor)

    def _on_threshold_changed(self, value: float) -> None:
        sensor = self._engine.sensors[self._selected_sensor_index]
        self._engine.set_threshold(sensor.name, value)
        # Move the threshold line immediately, even while stopped
        self._chart.update_chart(sensor, self._selected_sensor_index)

    def _on_reset(self) -> None:
        self._engine.reset()
        # Clear all sensor cards back to defaults
        for card, sensor in zip(self._sensor_cards, self._engine.sensors):
            card.update_sensor(sensor)
        # Clear the chart, keeping the threshold line visible
        selected = self._engine.sensors[self._selected_sensor_index]
        self._chart.clear(selected)
        self._status_bar.config(text="Reset — press Start to begin simulation")

    def _on_export(self) -> None:
        directory = filedialog.askdirectory(
            title="Select Export Directory",
            initialdir=os.path.expanduser("~"))
        if not directory:
            return
        try:
            path = CsvExporter.export(self._engine.sensors, directory)
            messagebox.showinfo("Export Successful", f"Saved to:\n{path}")
            self._status_bar.config(text=f"Exported → {path}")
        except Exception as exc:
            messagebox.showerror("Export Failed", str(exc))

    def _on_theme_toggle(self) -> None:
        self._theme_mgr.toggle()
        self._apply_theme()

    def _on_close(self) -> None:
        self._engine.stop()
        self.destroy()

    def _apply_theme(self) -> None:
        p = self._theme_mgr.palette
        self.config(bg=p.bg)
        self._recurse_bg(self, p.bg)
        self._status_lbl.config(bg=p.bg)
        self._status_bar.config(bg=p.status_bg, fg=p.fg_dim)
        self._chart.apply_palette(p)
        self._controls.apply_palette(p)
        for card in self._sensor_cards:
            card.apply_palette(p)
        self._on_status_changed(self._engine.is_running)

    def _recurse_bg(self, widget: tk.Widget, bg: str) -> None:
        try:
            if isinstance(widget, (tk.Frame, tk.Label)):
                widget.config(bg=bg)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._recurse_bg(child, bg)