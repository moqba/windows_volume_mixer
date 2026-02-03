from typing import Final

import win32api
import win32con
import win32gui
import pefile
from pathlib import Path
import psutil

LAUNCHERS: Final[set[str]] = {"steam.exe", "epicgameslauncher.exe", "battle.net.exe", "riotclientservices.exe",
                              "ubisoftconnect.exe"}
GAME_KEYWORDS: Final[set[str]] = {"game", "engine", "unreal", "unity"}


class DetectGame:
    def is_game(self):
        raise NotImplementedError()

    @staticmethod
    def looks_like_game(exe_path: str | Path):
        exe_path = Path(exe_path)
        pe = pefile.PE(exe_path)
        for entry in pe.FileInfo[0]:
            for st in entry.StringTable:
                text = " ".join(st.entries.values()).lower()
                if any(k in text for k in GAME_KEYWORDS):
                    return True
        return False

    @staticmethod
    def launched_by_launcher(proc: psutil.Process) -> bool:
        try:
            parent = proc.parent()
            if not parent:
                return False
            return parent.name().lower() in LAUNCHERS
        except psutil.Error:
            return False

    @staticmethod
    def is_fullscreen_window(hwnd) -> bool:
        if not win32gui.IsWindowVisible(hwnd):
            return False

        is_minimized_window = win32gui.IsIconic(hwnd)
        if is_minimized_window:
            return False

        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

        if style & win32con.WS_OVERLAPPEDWINDOW:
            return False

        rect = win32gui.GetWindowRect(hwnd)
        win_w = rect[2] - rect[0]
        win_h = rect[3] - rect[1]

        monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        mi = win32api.GetMonitorInfo(monitor)
        mon_rect = mi["Monitor"]

        mon_w = mon_rect[2] - mon_rect[0]
        mon_h = mon_rect[3] - mon_rect[1]

        return abs(win_w - mon_w) <= 5 and abs(win_h - mon_h) <= 5

