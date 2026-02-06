import threading
import sys
import webbrowser
import uvicorn
from typing import Final
import pystray
from pystray import MenuItem as item
from PIL import Image
from pathlib import Path

from windows_volume_mixer.base_path import BASE_PATH

HOST: Final[str] = "0.0.0.0"
PORT: Final[int] = 51000
URL: Final[str] = f"http://127.0.0.1:{PORT}"
ICON_PATH: Final[Path] = BASE_PATH / "core/mq_icon_mixer.ico"


def run_server():
    uvicorn.run(
        "volume_mixer_api:app",
        host=HOST,
        port=PORT,
        log_level="info",
        reload=False,
    )


server_thread = threading.Thread(
    target=run_server,
    daemon=True
)


def open_mq_mixer(icon, item):
    webbrowser.open(URL)


def quit_app(icon, item):
    icon.stop()
    sys.exit(0)


icon_image = Image.open(ICON_PATH)

menu = (
    item("Open MQ Mixer", open_mq_mixer),
    item("Quit", quit_app),
)

icon = pystray.Icon(
    "mq_mixer",
    icon_image,
    "MQ Mixer",
    menu
)

if __name__ == "__main__":
    server_thread.start()
    icon.run()
