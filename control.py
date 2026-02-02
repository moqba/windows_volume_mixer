from typing import Annotated

from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, AudioSession
from pydantic import BaseModel, Field


class Volume(BaseModel):
    value: Annotated[float, Field(ge=0, le=1)]

    @property
    def percentage(self) -> float:
        return self.value*100

    @classmethod
    def from_percentage(cls, percentage:float):
        return cls(value=percentage/100)


def get_volume(session: AudioSession) -> float:
    volume_iface = session._ctl.QueryInterface(ISimpleAudioVolume)
    return volume_iface.GetMasterVolume()


def set_volume(session: AudioSession, value: float) -> None:
    volume_iface = session._ctl.QueryInterface(ISimpleAudioVolume)
    volume_iface.SetMasterVolume(value, None)


def get_session_from_keyword(keyword: str) -> AudioSession:
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if not session.Process:
            continue
        if keyword.lower() in session.Process.name().lower():
            return session
    raise ValueError(f"Session not found for keyword {keyword}")
