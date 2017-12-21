@echo off
set dev=E:\github\skin.embuary
set target=skin.embuary
set htpc=\\NUCFRED\Kodi\portable_data\addons\skin.embuary
echo. 
echo Copying files
echo. 
XCOPY %dev% %target% /E /C /Q /I /Y
del /q /s %target%\*.pyo 
del /q /s %target%\*.pyc 
del /q /s %target%\*.psd 
del /q /s %target%\*.mo
rd /S /Q %target%\.git
TIMEOUT /T 4 /NOBREAK
repoupdate.bat