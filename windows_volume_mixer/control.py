from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, AudioSession

from windows_volume_mixer.volume import Volume


def get_volume(session: AudioSession) -> Volume:
    volume_iface = session._ctl.QueryInterface(ISimpleAudioVolume)
    return Volume(value=volume_iface.GetMasterVolume())


def set_volume(session: AudioSession, volume: Volume) -> None:
    volume_iface = session._ctl.QueryInterface(ISimpleAudioVolume)
    volume_iface.SetMasterVolume(volume.value, None)


def get_session_from_keyword(keyword: str) -> AudioSession:
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if not session.Process:
            continue
        if keyword.lower() in session.Process.name().lower():
            return session
    raise ValueError(f"Session not found for keyword {keyword}")
