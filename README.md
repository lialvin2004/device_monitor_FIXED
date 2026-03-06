# Device Monitor Dashboard

This is a desktop app I built that simulates live sensor readings for temperature, humidity, and pressure. It updates every second, shows a live chart, and highlights a warning when a reading crosses a threshold you can set with the slider. I went with Python and Tkinter (OPTION A) because it ships with Python so there's nothing extra to install for the GUI, and matplotlib handles the chart cleanly with the backend. I kept all the logic files completely separate from the UI so the core stuff is easy to test without needing a display.

The code is split into a model layer (sensor.py, simulation.py), a view layer (the widgets), and a controller (main_window.py) that wires everything together. The simulation runs on a background thread and uses callbacks to notify the UI, so Tkinter stays responsive. I also added CSV export, a dark/light theme toggle, and 28 unit tests as bonus features.

---

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

## Run Tests

```bash
python -m unittest test_all
```

## File Structure

```
├── main.py               Entry point
├── main_window.py        Controller — wires engine and widgets together
├── sensor.py             Sensor + SensorReading dataclasses
├── simulation.py         SimulationEngine + SensorFactory
├── exporter.py           CSV export (bonus)
├── theme.py              Dark/light palettes (bonus)
├── sensor_card.py        Card widget per sensor
├── chart_widget.py       Live matplotlib chart
├── controls_panel.py     Buttons, slider, dropdown
└── test_all.py           28 unit tests
```
##Design Patterns
```
All four patterns ended up in the code naturally. I used Observer so the simulation engine never has to know anything about the UI, it just fires callbacks and MainWindow decides what to do with them. MVC came from keeping sensor.py and simulation.py completely free of Tkinter imports so the logic stays totally separate from the display. Factory is just SensorFactory.create_defaults() in simulation.py, one method that builds all three sensors so there is a single place to change if I wanted to add more. Thread marshalling was necessary because the simulation runs on a background thread and Tkinter isn't thread-safe, so every UI update gets pushed back to the main thread with self.after(0, fn).
```
