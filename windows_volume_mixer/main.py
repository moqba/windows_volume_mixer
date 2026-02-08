import sys
import multiprocessing
import webbrowser
from multiprocessing import Process
from pathlib import Path
from typing import Final

import uvicorn
from PySide6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QObject, Slot

from windows_volume_mixer.base_path import BASE_PATH
from windows_volume_mixer.configuration_gui import ConfigWindow, fetch_config
from windows_volume_mixer.volume_mixer_api import volume_mixer_api


HOST: Final[str] = "0.0.0.0"
PORT: Final[int] = fetch_config().port
URL: Final[str] = f"http://127.0.0.1:{PORT}"
ICON_PATH: Final[Path] = BASE_PATH / "core/mq_icon_mixer.ico"


def run_server():
    uvicorn.run(
        volume_mixer_api,
        host=HOST,
        port=PORT,
        log_level="info",
        reload=False,
        log_config=None,
    )


class TrayController(QObject):
    def __init__(self, tray: QSystemTrayIcon, server_process: Process):
        super().__init__()
        self.tray = tray
        self.server_process = server_process
        self.config_window: ConfigWindow | None = None

    @Slot()
    def open_mq_mixer(self):
        webbrowser.open(URL)

    @Slot()
    def open_configurator(self):
        if self.config_window is None:
            self.config_window = ConfigWindow()

        self.config_window.show()
        self.config_window.raise_()
        self.config_window.activateWindow()

    @Slot()
    def quit_app(self):
        if self.server_process.is_alive():
            self.server_process.terminate()
            try:
                self.server_process.join(timeout=5)
            except Exception:
                self.server_process.kill()

        QApplication.quit()


def main():
    multiprocessing.freeze_support()

    server_process = Process(target=run_server, daemon=True)
    server_process.start()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    tray = QSystemTrayIcon(QIcon(str(ICON_PATH)))
    tray.setToolTip("MQ Mixer")

    menu = QMenu()
    controller = TrayController(tray, server_process)

    menu.addAction("Open MQ Mixer", controller.open_mq_mixer)
    menu.addAction("Settings", controller.open_configurator)
    menu.addSeparator()
    menu.addAction("Quit", controller.quit_app)

    tray.setContextMenu(menu)
    tray.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
