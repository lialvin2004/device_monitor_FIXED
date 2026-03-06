"""
theme.py
Colour palettes for dark and light themes. Pure data — no Tkinter imports.
"""

from dataclasses import dataclass
from enum import Enum, auto


class Theme(Enum):
    DARK = auto()
    LIGHT = auto()


@dataclass(frozen=True)
class Palette:
    bg: str;         bg_card: str;    bg_input: str
    border: str;     border_warn: str
    fg: str;         fg_dim: str;     fg_label: str
    accent: str;     accent_green: str; accent_red: str; accent_orange: str
    btn_bg: str;     btn_fg: str;     btn_active: str
    chart_bg: str;   chart_grid: str
    chart_line: str; chart_line2: str; chart_line3: str
    status_bg: str


DARK = Palette(
    bg="#0f1117",        bg_card="#1a1f2e",    bg_input="#1a1f2e",
    border="#2d3748",    border_warn="#fc8181",
    fg="#e2e8f0",        fg_dim="#718096",     fg_label="#a0aec0",
    accent="#63b3ed",    accent_green="#68d391", accent_red="#fc8181", accent_orange="#f6ad55",
    btn_bg="#2d3748",    btn_fg="#e2e8f0",     btn_active="#3d4f6e",
    chart_bg="#0f1117",  chart_grid="#1e2535",
    chart_line="#63b3ed", chart_line2="#68d391", chart_line3="#f6ad55",
    status_bg="#0a0d14",
)

LIGHT = Palette(
    bg="#f0f4f8",        bg_card="#ffffff",    bg_input="#ffffff",
    border="#e2e8f0",    border_warn="#e53e3e",
    fg="#1a202c",        fg_dim="#718096",     fg_label="#4a5568",
    accent="#2b6cb0",    accent_green="#276749", accent_red="#e53e3e", accent_orange="#c05621",
    btn_bg="#edf2f7",    btn_fg="#1a202c",     btn_active="#bee3f8",
    chart_bg="#ffffff",  chart_grid="#edf2f7",
    chart_line="#2b6cb0", chart_line2="#276749", chart_line3="#c05621",
    status_bg="#e2e8f0",
)

PALETTES = {Theme.DARK: DARK, Theme.LIGHT: LIGHT}


class ThemeManager:
    def __init__(self) -> None:
        self._current = Theme.DARK

    @property
    def current(self) -> Theme:
        return self._current

    @property
    def palette(self) -> Palette:
        return PALETTES[self._current]

    def toggle(self) -> "ThemeManager":
        self._current = Theme.LIGHT if self._current == Theme.DARK else Theme.DARK
        return self
