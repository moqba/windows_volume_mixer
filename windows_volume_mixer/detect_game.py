import psutil
import win32gui
import win32process
import win32con
import win32api

CPU_THRESHOLD = 5  # percent CPU usage to consider "active game"

GAME_CONFIRM_POLLS = 2
GAME_GONE_POLLS = 2

_candidate: str | None = None
_candidate_streak: int = 0
_confirmed: str | None = None
_gone_streak: int = 0


def is_borderless_or_fullscreen(hwnd: int) -> bool:
    if not win32gui.IsWindowVisible(hwnd):
        return False
    is_minimized = win32gui.IsIconic(hwnd)
    if is_minimized:
        return False

    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

    is_borderless = not (style & win32con.WS_OVERLAPPEDWINDOW) and not (ex_style & win32con.WS_EX_TOOLWINDOW)

    win_rect = win32gui.GetWindowRect(hwnd)
    monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    mon_info = win32api.GetMonitorInfo(monitor)
    mon_rect = mon_info["Monitor"]

    tolerance = 2
    is_size_match = (
            abs(win_rect[0] - mon_rect[0]) <= tolerance and
            abs(win_rect[1] - mon_rect[1]) <= tolerance and
            abs(win_rect[2] - mon_rect[2]) <= tolerance and
            abs(win_rect[3] - mon_rect[3]) <= tolerance
    )

    return is_borderless and is_size_match or style & win32con.WS_POPUP


def drop_exe(name: str) -> str:
    if name.lower().endswith(".exe"):
        return name[:-4]
    return name


def _detect_raw(cpu_threshold: float) -> str | None:
    """Single-shot detection with no debouncing."""
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


def get_active_game_process(cpu_threshold=CPU_THRESHOLD) -> str | None:
    global _candidate, _candidate_streak, _confirmed, _gone_streak

    raw = _detect_raw(cpu_threshold)

    if raw:
        if raw == _candidate:
            _candidate_streak += 1
        else:
            _candidate = raw
            _candidate_streak = 1
        _gone_streak = 0

        if _candidate_streak >= GAME_CONFIRM_POLLS:
            _confirmed = raw
    else:
        _gone_streak += 1
        if _gone_streak >= GAME_GONE_POLLS:
            _candidate = None
            _candidate_streak = 0
            _confirmed = None
            _gone_streak = 0

    return _confirmed
