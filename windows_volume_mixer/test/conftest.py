from typing import Final

from pycaw.utils import AudioSession
from pytest import fixture

from windows_volume_mixer.control import get_session_from_keyword

SAMPLE_APP: Final[str] = "spotify"


@fixture
def spotify_audio_session() -> AudioSession:
    return get_session_from_keyword("spotify")


@fixture
def discord_audio_session() -> AudioSession:
    return get_session_from_keyword("discord")
