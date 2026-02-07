import psutil
import win32gui
import win32process
import win32con
import win32api

CPU_THRESHOLD = 5  # percent CPU usage to consider “active game”


def is_borderless_or_fullscreen(hwnd: int) -> bool:
    if not win32gui.IsWindowVisible(hwnd):
        return False
    if win32gui.IsIconic(hwnd):  # minimized
        return False

    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

    # Borderless window detection
    borderless = not (style & win32con.WS_OVERLAPPEDWINDOW) and not (ex_style & win32con.WS_EX_TOOLWINDOW)

    # Window rect vs monitor rect
    win_rect = win32gui.GetWindowRect(hwnd)
    monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    mon_info = win32api.GetMonitorInfo(monitor)
    mon_rect = mon_info["Monitor"]

    TOL = 2  # allow small difference
    size_match = (
            abs(win_rect[0] - mon_rect[0]) <= TOL and
            abs(win_rect[1] - mon_rect[1]) <= TOL and
            abs(win_rect[2] - mon_rect[2]) <= TOL and
            abs(win_rect[3] - mon_rect[3]) <= TOL
    )

    return borderless and size_match or style & win32con.WS_POPUP


def drop_exe(name: str) -> str:
    if name.lower().endwith(".exe"):
        return name[:-4]
    return name


def get_active_game_process(cpu_threshold=CPU_THRESHOLD):
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None

    if not is_borderless_or_fullscreen(hwnd):
        return None

    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        proc = psutil.Process(pid)
        cpu = proc.cpu_percent(interval=0.1)
        if cpu >= cpu_threshold:
            return drop_exe(proc.name())
    except psutil.Error:
        return None

    return None