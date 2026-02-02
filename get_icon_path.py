from pathlib import Path
from PIL import Image
import win32gui
import win32ui
from pycaw.pycaw import AudioSession


def save_icon_from_session(session: AudioSession, dir: Path):
    exe_path = session.Process.exe()
    large, _ = win32gui.ExtractIconEx(exe_path, 0)
    if not large:
        return
    hicon = large[0]
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, 256, 256)

    memdc=hdc.CreateCompatibleDc()
    memdc.SelectObject(hbmp)
    memdc.DrawIcon((0,0), hicon)

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

    img.save(dir / "new_image.png")
