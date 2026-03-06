"""
test_all.py
Unit tests for the data/logic layer. No Tkinter or display required.

Run with:
    python -m pytest test_all.py -v
or:
    python -m unittest test_all
"""

import csv
import os
import sys
import tempfile
import unittest

# Allow imports from the same directory
sys.path.insert(0, os.path.dirname(__file__))

from sensor import Sensor, SensorReading
from exporter import CsvExporter


# ── Sensor tests ───────────────────────────────────────────────────────────

class TestSensorInitialState(unittest.TestCase):
    def setUp(self):
        self.sensor = Sensor("Temperature", "°C", 0.0, 100.0, 75.0)

    def test_history_empty_on_creation(self):
        self.assertEqual(len(self.sensor.history), 0)

    def test_current_value_zero_when_empty(self):
        self.assertEqual(self.sensor.current_value, 0.0)

    def test_not_above_threshold_when_empty(self):
        self.assertFalse(self.sensor.is_above_threshold)


class TestSensorTick(unittest.TestCase):
    def setUp(self):
        self.sensor = Sensor("Humidity", "%", 20.0, 80.0, 60.0)

    def test_tick_returns_reading(self):
        self.assertIsInstance(self.sensor.tick(1.0), SensorReading)

    def test_tick_appends_to_history(self):
        self.sensor.tick(1.0)
        self.assertEqual(len(self.sensor.history), 1)

    def test_multiple_ticks_grow_history(self):
        for _ in range(5):
            self.sensor.tick(1.0)
        self.assertEqual(len(self.sensor.history), 5)

    def test_value_within_bounds(self):
        for _ in range(50):
            r = self.sensor.tick(1.0)
            self.assertGreaterEqual(r.value, self.sensor.min_value)
            self.assertLessEqual(r.value, self.sensor.max_value)

    def test_timestamp_increases(self):
        r1 = self.sensor.tick(1.0)
        r2 = self.sensor.tick(1.0)
        self.assertGreater(r2.timestamp, r1.timestamp)

    def test_current_value_reflects_latest_tick(self):
        r = self.sensor.tick(1.0)
        self.assertEqual(self.sensor.current_value, r.value)


class TestSensorHistoryLimit(unittest.TestCase):
    def test_history_capped_at_limit(self):
        s = Sensor("P", "hPa", 980.0, 1040.0, 1020.0, history_limit=10)
        for _ in range(25):
            s.tick(1.0)
        self.assertLessEqual(len(s.history), 10)

    def test_oldest_entry_dropped_first(self):
        s = Sensor("P", "hPa", 980.0, 1040.0, 1020.0, history_limit=3)
        ticks = [s.tick(1.0) for _ in range(5)]
        self.assertAlmostEqual(s.history[0].timestamp, ticks[2].timestamp, places=5)
        self.assertAlmostEqual(s.history[-1].timestamp, ticks[4].timestamp, places=5)


class TestSensorThreshold(unittest.TestCase):
    def _sensor_with_value(self, value: float) -> Sensor:
        s = Sensor("Test", "x", 0.0, 200.0, 100.0)
        s.history.append(SensorReading(value=value, timestamp=1.0))
        return s

    def test_above_threshold(self):
        self.assertTrue(self._sensor_with_value(110.0).is_above_threshold)

    def test_below_threshold(self):
        self.assertFalse(self._sensor_with_value(90.0).is_above_threshold)

    def test_exactly_at_threshold_not_above(self):
        self.assertFalse(self._sensor_with_value(100.0).is_above_threshold)


class TestSensorReset(unittest.TestCase):
    def test_reset_clears_history(self):
        s = Sensor("T", "°C", 0.0, 100.0, 50.0)
        for _ in range(10):
            s.tick(1.0)
        s.reset()
        self.assertEqual(len(s.history), 0)

    def test_reset_restarts_elapsed(self):
        s = Sensor("T", "°C", 0.0, 100.0, 50.0)
        s.tick(5.0)
        s.reset()
        r = s.tick(1.0)
        self.assertAlmostEqual(r.timestamp, 1.0, places=5)


class TestSensorHistoryProperties(unittest.TestCase):
    def _filled(self, n: int) -> Sensor:
        s = Sensor("T", "°C", 0.0, 100.0, 50.0)
        for _ in range(n):
            s.tick(1.0)
        return s

    def test_history_values_length(self):
        self.assertEqual(len(self._filled(7).history_values), 7)

    def test_history_timestamps_length(self):
        self.assertEqual(len(self._filled(7).history_timestamps), 7)

    def test_values_and_timestamps_parallel(self):
        s = Sensor("T", "°C", 0.0, 100.0, 50.0)
        readings = [s.tick(1.0) for _ in range(5)]
        for val, ts, r in zip(s.history_values, s.history_timestamps, readings):
            self.assertEqual(val, r.value)
            self.assertAlmostEqual(ts, r.timestamp, places=5)


# ── CsvExporter tests ──────────────────────────────────────────────────────

def _make_sensor(name: str, values: list) -> Sensor:
    s = Sensor(name, "u", 0.0, 200.0, 100.0)
    for v in values:
        s.tick(1.0)
        s.history[-1].value = v
    return s


class TestCsvExporter(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()

    def test_creates_file(self):
        path = CsvExporter.export([_make_sensor("T", [20.0])], self._tmpdir)
        self.assertTrue(os.path.isfile(path))

    def test_has_threshold_row(self):
        path = CsvExporter.export([_make_sensor("Temp", [20.0])], self._tmpdir)
        with open(path, newline="") as f:
            first_row = next(csv.reader(f))
        self.assertEqual(first_row[0], "Threshold")

    def test_file_has_header(self):
        path = CsvExporter.export([_make_sensor("Temp", [20.0])], self._tmpdir)
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader)          # skip threshold row
            header = next(reader)
        self.assertIn("Time (s)", header)
        self.assertTrue(any("Temp" in col for col in header))

    def test_has_warning_column_in_header(self):
        path = CsvExporter.export([_make_sensor("Temp", [20.0])], self._tmpdir)
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader)
            header = next(reader)
        self.assertTrue(any("Warning" in col for col in header))

    def test_row_count_matches_history(self):
        path = CsvExporter.export([_make_sensor("T", [10.0, 20.0, 30.0])], self._tmpdir)
        with open(path, newline="") as f:
            rows = list(csv.reader(f))
        # 1 threshold row + 1 header + 3 data rows = 5
        self.assertEqual(len(rows), 5)

    def test_warn_flag_above_threshold(self):
        s = _make_sensor("T", [150.0])   # threshold=100, value=150
        path = CsvExporter.export([s], self._tmpdir)
        with open(path, newline="") as f:
            rows = list(csv.reader(f))
        self.assertEqual(rows[2][2], "WARN")

    def test_ok_flag_below_threshold(self):
        s = _make_sensor("T", [50.0])    # threshold=100, value=50
        path = CsvExporter.export([s], self._tmpdir)
        with open(path, newline="") as f:
            rows = list(csv.reader(f))
        self.assertEqual(rows[2][2], "ok")

    def test_multiple_sensors_exported(self):
        sensors = [_make_sensor("T", [10.0, 20.0]), _make_sensor("H", [50.0, 55.0])]
        path = CsvExporter.export(sensors, self._tmpdir)
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader)
            header = next(reader)
        # Time + (value + warning) * 2 sensors = 5 columns
        self.assertEqual(len(header), 5)

    def test_filename_contains_timestamp(self):
        path = CsvExporter.export([_make_sensor("T", [10.0])], self._tmpdir)
        name = os.path.basename(path)
        self.assertTrue(name.startswith("sensor_export_"))
        self.assertTrue(name.endswith(".csv"))


if __name__ == "__main__":
    unittest.main()