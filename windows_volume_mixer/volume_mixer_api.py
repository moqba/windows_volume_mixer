import asyncio

from fastapi import FastAPI, Request, HTTPException
from tempfile import TemporaryDirectory
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import StreamingResponse, FileResponse

from windows_volume_mixer.base_path import BASE_PATH
from windows_volume_mixer.control import get_session_from_keyword, get_volume, set_volume
from windows_volume_mixer.get_icon_path import save_icon_from_session
from windows_volume_mixer.volume import Volume


class SetVolumeData(BaseModel):
    app: str
    value: float


def volume_mixer_api() -> FastAPI:
    app = FastAPI()

    app.mount("/static", StaticFiles(directory=BASE_PATH / "landing_page", html=True), name="static")

    @app.get("/")
    def landing():
        return FileResponse(BASE_PATH / "landing_page/index.html")

    async def volume_event(app: str):
        try:
            audio_sessions = get_session_from_keyword(keyword=app)
            while True:
                if not audio_sessions:
                    return
                volume = get_volume(audio_sessions[0]).value
                yield f"data: {volume}\n\n"
                await asyncio.sleep(1)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"{e}")

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

    @app.get("/icon/{app}")
    async def api_get_icon(app: str):
        audio_sessions = get_session_from_keyword(keyword=app)
        if not audio_sessions:
            raise HTTPException(status_code=404, detail="Application not open")
        with TemporaryDirectory() as temp_dir:
            icon_path = save_icon_from_session(session=audio_sessions[0], output_dir=temp_dir)
            if icon_path:
                return FileResponse(icon_path, media_type="image/png")
        raise HTTPException(status_code=404, detail=f"Couldn't fetch icon for app {app}")

    @app.put("/set-volume")
    async def api_set_volume(set_volume_data: SetVolumeData):
        try:
            volume = Volume(value=set_volume_data.value)
            audio_sessions = get_session_from_keyword(keyword=set_volume_data.app)
            for audio_session in audio_sessions:
                set_volume(session=audio_session, volume=volume)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"{e}")

    return app
