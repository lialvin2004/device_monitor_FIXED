"""
sensor.py
Data layer: Sensor model with no UI dependencies whatsoever.
"""

import math
import random
from dataclasses import dataclass, field
from typing import List


@dataclass
class SensorReading:
    """A single timestamped reading for one sensor."""
    value: float
    timestamp: float  # seconds since simulation start


@dataclass
class Sensor:
    """
    Represents a single simulated sensor.

    Generates values using a sine wave + Gaussian noise so trends are visible
    on the chart while still feeling live.  All threshold and history state
    lives here — the UI only reads, never writes, to these fields directly.
    """
    name: str
    unit: str
    min_value: float
    max_value: float
    threshold: float
    wave_period: float = 20.0
    history_limit: int = 30

    history: List[SensorReading] = field(default_factory=list)
    _elapsed: float = field(default=0.0, init=False, repr=False)

    def tick(self, delta_seconds: float) -> SensorReading:
        """Advance simulation by *delta_seconds* and return the new reading."""
        self._elapsed += delta_seconds
        value = self._generate_value()
        reading = SensorReading(value=value, timestamp=self._elapsed)
        self.history.append(reading)
        if len(self.history) > self.history_limit:
            self.history.pop(0)
        return reading

    def reset(self) -> None:
        self.history.clear()
        self._elapsed = 0.0

    @property
    def current_value(self) -> float:
        return self.history[-1].value if self.history else 0.0

    @property
    def is_above_threshold(self) -> bool:
        return self.current_value > self.threshold

    @property
    def history_values(self) -> List[float]:
        return [r.value for r in self.history]

    @property
    def history_timestamps(self) -> List[float]:
        return [r.timestamp for r in self.history]

    def _generate_value(self) -> float:
        mid = (self.min_value + self.max_value) / 2
        amplitude = (self.max_value - self.min_value) / 2 * 0.7
        sine = math.sin(2 * math.pi * self._elapsed / self.wave_period)
        noise = random.gauss(0, amplitude * 0.15)
        raw = mid + amplitude * sine + noise
        return round(max(self.min_value, min(self.max_value, raw)), 2)
