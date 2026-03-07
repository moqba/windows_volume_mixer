from logging import getLogger
from random import randint

from pycaw.utils import AudioSession

from windows_volume_mixer.control import get_volume, set_volume
from windows_volume_mixer.test.conftest import SAMPLE_APP
from windows_volume_mixer.volume import Volume

logger = getLogger(__name__)


def test_set_get_volume(spotify_audio_session: AudioSession):
    expected_volume = Volume.from_percentage(randint(0, 100))
    set_volume(spotify_audio_session, volume=expected_volume)
    volume = get_volume(spotify_audio_session)
    logger.info("Volume for app %s is %s %", SAMPLE_APP, volume)
    assert volume == expected_volume