import multiprocessing
import threading
import sys
import webbrowser
from multiprocessing import Process

import uvicorn
from typing import Final
import pystray
from pystray import MenuItem as item
from PIL import Image
from pathlib import Path

from windows_volume_mixer.base_path import BASE_PATH
from windows_volume_mixer.volume_mixer_api import volume_mixer_api

HOST: Final[str] = "0.0.0.0"
PORT: Final[int] = 51000
URL: Final[str] = f"http://127.0.0.1:{PORT}"
ICON_PATH: Final[Path] = BASE_PATH / "core/mq_icon_mixer.ico"



def run_server():
    uvicorn.run(
        volume_mixer_api,
        host=HOST,
        port=PORT,
        log_level="info",
        reload=False,
        log_config=None
    )


server_process = Process(target=run_server)


def open_mq_mixer(icon, item):
    webbrowser.open(URL)


def quit_app(icon, item):
    icon.stop()
    server_process.terminate()
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
    multiprocessing.freeze_support()
    server_process.start()
    icon.run()
