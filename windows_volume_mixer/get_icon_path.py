import win32gui
import win32ui
import win32con
from PIL import Image
from pathlib import Path


def save_icon_from_session(session, output_dir: Path | str) -> Path | None:
    """
    Save the largest available icon from the given AudioSession's process.
    Returns the path to the saved PNG or None if no icon found.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    exe_path = Path(session.Process.exe())
    exe_name = exe_path.stem
    out_path = output_dir / f"{exe_name}.png"

    if out_path.exists():
        return out_path

    hicon = extract_largest_icon(exe_path)
    if hicon is None:
        return None

    img = hicon_to_image(hicon)
    img.save(out_path)
    return out_path


def extract_largest_icon(exe_path: Path):
    """
    Enumerates all icons in the EXE and returns the handle of the largest one.
    """
    icons = []
    i = 0
    while True:
        large, small = win32gui.ExtractIconEx(str(exe_path), i)
        if not large and not small:
            break

        for h in large + small:
            try:
                info = win32gui.GetIconInfo(h)
                bmp = win32ui.CreateBitmapFromHandle(info[3])
                width = bmp.GetInfo()["bmWidth"]
                height = bmp.GetInfo()["bmHeight"]
                icons.append((width * height, h))  # sort by area
            except Exception:
                pass

        i += 1

    if not icons:
        return None

    _, hicon = max(icons, key=lambda x: x[0])
    return hicon


def hicon_to_image(hicon) -> Image:
    """
    Converts an HICON to a PIL Image at its native size, preserving transparency.
    """
    # Get native icon size
    info = win32gui.GetIconInfo(hicon)
    bmp = win32ui.CreateBitmapFromHandle(info[3])
    width = bmp.GetInfo()["bmWidth"]
    height = bmp.GetInfo()["bmHeight"]

    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, width, height)

    memdc = hdc.CreateCompatibleDC()
    memdc.SelectObject(hbmp)

    win32gui.DrawIconEx(
        memdc.GetSafeHdc(),
        0, 0,
        hicon,
        width, height,
        0, None,
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
    return img
