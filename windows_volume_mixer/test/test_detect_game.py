from pycaw.utils import AudioSession

from windows_volume_mixer.control import SessionHelper
from windows_volume_mixer.detect_game import DetectGame


class TestDetectGame:
    def test_looks_like_game(self, spotify_audio_session: AudioSession):
        session_helper = SessionHelper(audio_session=spotify_audio_session)
        DetectGame.looks_like_game(exe_path=session_helper.exe_path)

    def test_launched_by_launcher(self, spotify_audio_session: AudioSession):
        session_helper = SessionHelper(audio_session=spotify_audio_session)
        DetectGame.launched_by_launcher(proc=session_helper.proc)

    def test_is_fullscreen_window(self, spotify_audio_session: AudioSession):
        session_helper = SessionHelper(audio_session=spotify_audio_session)
        DetectGame.is_fullscreen_window(hwnd=session_helper.hwnds[0])