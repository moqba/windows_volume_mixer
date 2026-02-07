from pathlib import Path
from typing import Final

import win32con
from PIL import Image
import win32gui
import win32ui
from pycaw.pycaw import AudioSession

ICON_WIDTH: Final[int] = 56
ICON_HEIGHT: Final[int] = 56


def save_icon_from_session(session: AudioSession, output_dir: Path | str) -> Path:
    output_dir = Path(output_dir)
    exe_path = Path(session.Process.exe())
    exe_name = exe_path.stem
    large, _ = win32gui.ExtractIconEx(str(exe_path), 0)
    if not large:
        return
    hicon = large[0]
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, ICON_WIDTH, ICON_HEIGHT)

    memdc = hdc.CreateCompatibleDC()
    memdc.SelectObject(hbmp)
    win32gui.DrawIconEx(
        memdc.GetSafeHdc(),
        0,
        0,
        hicon,
        ICON_WIDTH,
        ICON_HEIGHT,
        0,
        None,
        win32con.DI_NORMAL,
    )

    bmpinfo = hbmp.GetInfo()
    bmpstr = hbmp.GetBitmapBits(True)
    img = Image.frombuffer(
        "RGBA",
        (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
        bmpstr,
        "raw",
        "BGRA",
        0,
        1,
    )

    img.save(output_dir / f"{exe_name}.png")
    return output_dir / f"{exe_name}.png"
