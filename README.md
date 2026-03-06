# Device Monitor Dashboard

A desktop app displaying simulated sensor data (temperature, humidity, pressure) with a live chart, threshold warnings, and controls.

**Option A: Python 3 + Tkinter + matplotlib**.

---

## Why Tkinter?

Tkinter ships with Python's standard library so no extra GUI dependencies. It maps cleanly onto OOP: each widget is a class, layouts compose through Frame nesting, and the event loop integrates naturally with `threading.Timer` for background simulation. Matplotlib's `FigureCanvasTkAgg` backend embeds a fully-featured chart with one import. This stack keeps the logic files completely free of any UI dependency, so unit tests run without a display.

---

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> **Linux note**: if Tkinter is missing, run `sudo apt install python3-tk`

### 2. Start the app

```bash
python main.py
```

### 3. Run unit tests (no display needed)

```bash
python -m pytest test_all.py -v
# or without pytest:
python -m unittest test_all
```

---

## File Structure

Everything lives in one folder — no sub-packages.

```
device_monitor/
├── main.py             Entry point
├── main_window.py      MainWindow (tk.Tk) — Controller, wires everything
├── sensor.py           Sensor + SensorReading dataclasses  (no UI imports)
├── simulation.py       SimulationEngine + SensorFactory    (no UI imports)
├── exporter.py         CsvExporter                         (no UI imports)
├── theme.py            Palette dataclass + ThemeManager    (no UI imports)
├── sensor_card.py      SensorCard widget — one tile per sensor
├── chart_widget.py     ChartWidget — matplotlib line chart
├── controls_panel.py   ControlsPanel — all buttons/slider/dropdown
├── test_all.py         24 unit tests (Sensor + CsvExporter)
└── requirements.txt
```

---

## Architecture (MVC)

| Role | Files |
|---|---|
| **Model** | `sensor.py`, `simulation.py`, `exporter.py`, `theme.py` |
| **View** | `sensor_card.py`, `chart_widget.py`, `controls_panel.py` |
| **Controller** | `main_window.py` |

---

## Design Patterns

| Pattern | Where | One-line explanation |
|---|---|---|
| **Observer** | `SimulationEngine` → `MainWindow` | Engine holds callback lists; `MainWindow` registers handlers so the engine never references widgets. |
| **MVC** | Whole app | Model files have zero Tkinter imports; View widgets contain no logic. |
| **Factory** | `SensorFactory.create_defaults()` | Centralises sensor construction in one place. |
| **Thread marshalling** | `MainWindow._connect_engine()` | Engine callbacks are wrapped in `root.after(0, fn)` to safely push updates onto the Tk main thread. |

---

## Architecture Diagram

```
main.py
  └─ MainWindow(tk.Tk)          ← Controller
       ├─ SimulationEngine       ← Model (threading.Timer, no UI)
       │    └─ Sensor × 3       ← Model (SensorFactory builds these)
       ├─ SensorCard × 3        ← View
       ├─ ChartWidget            ← View (matplotlib embedded)
       └─ ControlsPanel          ← View (callbacks only, no logic)

Thread safety:
  SimulationEngine._on_tick()  ──(daemon thread)──►  root.after(0, fn)  ──►  Tk main thread
```

---

## Bonus Features

| Feature | File |
|---|---|
| Export sensor history to CSV | `exporter.py` — triggered by ⬇ Export CSV button |
| Unit tests for logic layer | `test_all.py` — 24 tests, no display required |
| Dark / Light theme toggle | `theme.py` — triggered by ◑ Toggle Theme button |

---

## Known Issues / Future Improvements

- **matplotlib flicker**: `draw_idle()` minimises redraws but blitting would eliminate them entirely.
- **High-DPI on Windows**: without a DPI manifest, Tkinter may appear blurry on 4K displays.
- **Multi-series chart**: currently shows one sensor at a time; overlaying all three would aid correlation.
- **Persistent settings**: theme and threshold values reset on close; `configparser` could persist them.
