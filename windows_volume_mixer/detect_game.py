from typing import Final

import win32con
import win32gui
from screeninfo import get_monitors
import pefile
from pathlib import Path
import psutil

LAUNCHERS: Final[set[str]] = {"steam.exe", "epicgameslauncher.exe", "battle.net.exe", "riotclientservices.exe",
                              "ubisoftconnect.exe"}
GAME_KEYWORDS: Final[set[str]] = {"game", "engine", "unreal", "unity"}


class DetectGame:
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
    def launched_by_launcher(proc) -> bool:
        try:
            parent = proc.parent()
            return parent and parent.name().lower() in LAUNCHERS
        except psutil.Error:
            return False

    @staticmethod
    def is_fullscreen_window(hwnd) -> bool:
        if not win32gui.IsWindowVisible(hwnd):
            return False
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        if style & win32gui.GetWindowRect(hwnd):
            return False

        rect = win32gui.GetWindowRect(hwnd)
        win_w = rect[2] - rect[0]
        win_h = rect[3] - rect[1]
        for monitor in get_monitors():
            mw, mh = monitor.width, monitor.height
            if abs(win_w - mw) <= 10 and abs(win_h - mh) <= 10:
                return True
        return False
