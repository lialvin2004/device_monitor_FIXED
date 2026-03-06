"""
simulation.py
SimulationEngine drives sensors via a repeating threading.Timer and notifies
the UI through registered callbacks (Observer pattern).

Design patterns:
  Observer  — on_tick() / on_status_changed() registration
  Factory   — SensorFactory.create_defaults()
"""

import threading
from typing import Callable, List

from sensor import Sensor


class SensorFactory:
    """Creates the default set of sensors for the dashboard."""

    @staticmethod
    def create_defaults() -> List[Sensor]:
        return [
            Sensor("Temperature", "°C",  min_value=15.0,  max_value=95.0,  threshold=75.0,  wave_period=18.0),
            Sensor("Humidity",    "%",   min_value=20.0,  max_value=90.0,  threshold=70.0,  wave_period=25.0),
            Sensor("Pressure",    "hPa", min_value=900.0, max_value=1100.0, threshold=1045.0, wave_period=35.0),
        ]


class SimulationEngine:
    """
    Drives sensor simulation at a fixed tick rate.

    Threading note: callbacks fire on a daemon thread. The MainWindow wraps
    them in root.after(0, fn) to marshal updates back to the Tk main thread.
    """

    TICK_INTERVAL_S: float = 1.0

    def __init__(self) -> None:
        self._sensors: List[Sensor] = SensorFactory.create_defaults()
        self._running: bool = False
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()
        self._tick_callbacks: List[Callable[[List[Sensor]], None]] = []
        self._status_callbacks: List[Callable[[bool], None]] = []

    def on_tick(self, callback: Callable[[List[Sensor]], None]) -> None:
        self._tick_callbacks.append(callback)

    def on_status_changed(self, callback: Callable[[bool], None]) -> None:
        self._status_callbacks.append(callback)

    @property
    def sensors(self) -> List[Sensor]:
        return self._sensors

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        with self._lock:
            if not self._running:
                self._running = True
                self._schedule_tick()
        self._notify_status(True)

    def stop(self) -> None:
        with self._lock:
            if self._running:
                self._running = False
                if self._timer:
                    self._timer.cancel()
                    self._timer = None
        self._notify_status(False)

    def toggle(self) -> None:
        self.stop() if self._running else self.start()

    def reset(self) -> None:
        self.stop()
        for sensor in self._sensors:
            sensor.reset()
        self._notify_tick()

    def set_threshold(self, sensor_name: str, value: float) -> None:
        for sensor in self._sensors:
            if sensor.name == sensor_name:
                sensor.threshold = value
                return

    def _schedule_tick(self) -> None:
        self._timer = threading.Timer(self.TICK_INTERVAL_S, self._on_tick)
        self._timer.daemon = True
        self._timer.start()

    def _on_tick(self) -> None:
        with self._lock:
            if not self._running:
                return
            for sensor in self._sensors:
                sensor.tick(self.TICK_INTERVAL_S)
        self._notify_tick()
        with self._lock:
            if self._running:
                self._schedule_tick()

    def _notify_tick(self) -> None:
        for cb in self._tick_callbacks:
            cb(self._sensors)

    def _notify_status(self, running: bool) -> None:
        for cb in self._status_callbacks:
            cb(running)
