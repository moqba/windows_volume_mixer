import asyncio

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from windows_volume_mixer.control import get_session_from_keyword, get_volume, set_volume
from windows_volume_mixer.volume import Volume

app = FastAPI()


#app.mount("/", StaticFiles(directory="landing_page", html=True), name="static")


class SetVolumeData(BaseModel):
    app: str
    value: float


async def volume_event(app: str):
    audio_sessions = get_session_from_keyword(keyword=app)
    while True:
        volume = get_volume(audio_sessions[0]).value
        yield f"data: {volume}\n\n"
        await asyncio.sleep(1)


@app.get("/volume/{app}")
async def stream_volume(app: str, request: Request):
    async def stream_until_disconnect():
        try:
            async for data in volume_event(app):
                if await request.is_disconnected():
                    break
                yield data
        except asyncio.CancelledError:
            pass

    try:
        return StreamingResponse(stream_until_disconnect(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")


@app.put("/set-volume")
async def api_set_volume(set_volume_data: SetVolumeData):
    try:
        volume = Volume(value=set_volume_data.value)
        audio_sessions = get_session_from_keyword(keyword=set_volume_data.app)
        for audio_session in audio_sessions:
            set_volume(session=audio_session, volume=volume)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")
