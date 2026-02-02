from pathlib import Path
from tempfile import tempdir

from pycaw.utils import AudioSession
from pytest import fixture

from windows_volume_mixer.get_icon_path import save_icon_from_session


@fixture
def icon_dir() -> Path:
    return Path(__file__).parent


def test_save_icon_from_session(icon_dir: Path, spotify_audio_session: AudioSession):
    save_icon_from_session(session=spotify_audio_session, dir=icon_dir)


def test_save_icon_from_session_discord(icon_dir: Path, discord_audio_session: AudioSession):
    save_icon_from_session(session=discord_audio_session, dir=icon_dir)
