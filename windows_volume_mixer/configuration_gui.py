import json
from pathlib import Path
from typing import Dict

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QCheckBox, QPushButton, QFrame,
    QMessageBox
)
from PySide6.QtCore import Qt

from pydantic import BaseModel, ValidationError, Field

CONFIG_PATH = Path("config.json")


class SliderConfig(BaseModel):
    slider_1: str = "game"
    slider_2: str = "spotify"
    slider_3: str = "chrome"
    slider_4: str = "discord"


class AppConfig(BaseModel):
    auto_start: bool = False
    sliders: SliderConfig = SliderConfig()
    port: int = Field(..., gt=0, lt=65536)

    @property
    def parsed_sliders(self):
        return [str(slider[1]) for slider in self.sliders]


DEFAULT_CONFIG = AppConfig(port=51000)


def fetch_config():
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG
    try:
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        config = AppConfig.model_validate(raw)
        return config
    except (json.JSONDecodeError, ValidationError):
        return DEFAULT_CONFIG


# --------------------
# GUI
# --------------------

class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration")
        self.setFixedWidth(420)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)

        title = QLabel("Application Configuration")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        self.auto_start_checkbox = QCheckBox("Auto load at Windows startup")
        main_layout.addWidget(self.auto_start_checkbox)

        main_layout.addWidget(self._separator())

        self.slider_inputs: Dict[str, QLineEdit] = {}
        defaults = [
            ("Slider 1", "slider_1"),
            ("Slider 2", "slider_2"),
            ("Slider 3", "slider_3"),
            ("Slider 4", "slider_4"),
        ]

        for label, key in defaults:
            layout, input_box = self._text_field(label)
            self.slider_inputs[key] = input_box
            main_layout.addLayout(layout)

        main_layout.addWidget(self._separator())

        self.port_input_layout, self.port_input = self._text_field("Port")
        main_layout.addLayout(self.port_input_layout)

        main_layout.addWidget(self._separator())

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.save_config)
        cancel_button.clicked.connect(self.close)

        ok_button.setDefault(True)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        self.load_config()

    # --------------------
    # UI helpers
    # --------------------

    def _text_field(self, label_text):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        input_box = QLineEdit()

        label.setFixedWidth(80)
        layout.addWidget(label)
        layout.addWidget(input_box)

        return layout, input_box

    def _separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    # --------------------
    # Config handling
    # --------------------

    def load_config(self):
        config = fetch_config()
        self.apply_config_to_ui(config)

    def apply_config_to_ui(self, config: AppConfig):
        self.auto_start_checkbox.setChecked(config.auto_start)

        self.slider_inputs["slider_1"].setText(config.sliders.slider_1)
        self.slider_inputs["slider_2"].setText(config.sliders.slider_2)
        self.slider_inputs["slider_3"].setText(config.sliders.slider_3)
        self.slider_inputs["slider_4"].setText(config.sliders.slider_4)

        self.port_input.setText(str(config.port))

    def save_config(self):
        if not self.port_input.text().strip():
            QMessageBox.warning(self, "Invalid configuration", "Port cannot be empty")
            return

        try:
            config = AppConfig(
                auto_start=self.auto_start_checkbox.isChecked(),
                sliders=SliderConfig(
                    slider_1=self.slider_inputs["slider_1"].text(),
                    slider_2=self.slider_inputs["slider_2"].text(),
                    slider_3=self.slider_inputs["slider_3"].text(),
                    slider_4=self.slider_inputs["slider_4"].text(),
                ),
                port=int(self.port_input.text()),
            )
        except (ValidationError, ValueError) as e:
            QMessageBox.critical(self, "Invalid configuration", str(e))
            return

        CONFIG_PATH.write_text(
            json.dumps(config.model_dump(), indent=4),
            encoding="utf-8",
        )

        self.close()