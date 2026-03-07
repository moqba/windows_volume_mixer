cd %~dp0
call .\.venv\Scripts\activate.bat
pyinstaller --onefile --noconsole ^
--name "MqMixer" ^
--add-data="windows_volume_mixer/core/mq_icon_mixer.ico;windows_volume_mixer/core" ^
--add-data="windows_volume_mixer/landing_page;windows_volume_mixer/landing_page" ^
--icon=windows_volume_mixer/core/mq_icon_mixer.ico ^
--collect-all uvicorn ^
windows_volume_mixer/main.py
pause