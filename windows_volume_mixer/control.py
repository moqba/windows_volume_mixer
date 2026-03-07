from dataclasses import dataclass
from pathlib import Path

import psutil
import win32gui
import win32process
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, AudioSession

from windows_volume_mixer.volume import Volume


def get_volume(session: AudioSession) -> Volume:
    volume_iface = session._ctl.QueryInterface(ISimpleAudioVolume)
    return Volume(value=volume_iface.GetMasterVolume())


def set_volume(session: AudioSession, volume: Volume) -> None:
    volume_iface = session._ctl.QueryInterface(ISimpleAudioVolume)
    volume_iface.SetMasterVolume(volume.value, None)


def get_session_from_keyword(keyword: str) -> list[AudioSession]:
    sessions = AudioUtilities.GetAllSessions()
    matching_sessions = []
    for session in sessions:
        if not session.Process:
            continue
        if keyword.lower() in session.Process.name().lower():
            matching_sessions.append(session)
    return matching_sessions


@dataclass
class SessionHelper:
    audio_session: AudioSession

    @property
    def exe_path(self) -> Path:
        return Path(self.audio_session.Process.exe())

    @property
    def proc(self) -> psutil.Process:
        return psutil.Process(self.audio_session.ProcessId)

    @property
    def hwnds(self) -> list[int]:
        hwnds = []
        pid = self.audio_session.ProcessId

        def callback(hwnd, _):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                hwnds.append(hwnd)

        win32gui.EnumWindows(callback, None)
        return hwnds
