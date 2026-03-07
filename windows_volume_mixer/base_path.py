import os
from pathlib import Path

BASE_PATH = Path(__file__).parent
APP_DATA = Path(os.environ["APPDATA"]) / "mq_mixer"
APP_DATA.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = APP_DATA/"mq_config.json"
