@echo off
setlocal enabledelayedexpansion
set TOOLS=%~dp0tools
set SOURCE=%~dp0
set GIT=C:\Program Files\Git\bin
echo. ^_  ^_^_        ^_ ^_   ^_^_^_                 ^_   ^_          ^_      ^_
echo.^| ^|/ ^/^_^_^_  ^_^_^| ^(^_^) ^| ^_ ^\^_^_^_ ^_ ^_^_  ^_^_^_  ^| ^| ^| ^|^_ ^_^_  ^_^_^| ^|^_^_ ^_^| ^|^_ ^_^_^_ ^_ ^_ 
echo.^| ^' ^<^/ ^_ ^\^/ ^_^` ^| ^| ^|   ^/ ^-^_^) ^'^_ ^\^/ ^_ ^\ ^| ^|^_^| ^| ^'^_ ^\^/ ^_^` ^/ ^_^` ^|  ^_^/ ^-^_^) ^'^_^|
echo.^|^_^|^\^_^\^_^_^_^/^\^_^_^,^_^|^_^| ^|^_^|^_^\^_^_^_^| ^.^_^_^/^\^_^_^_^/  ^\^_^_^_^/^| ^.^_^_^/^\^_^_^,^_^\^_^_^,^_^|^\^_^_^\^_^_^_^|^_^|  
echo.                           ^|^_^|               ^|^_^|                          
echo.by sualfred
echo.
TIMEOUT /T 2 /NOBREAK
goto :updatefiles

:updatefiles
echo.
echo.
echo.[ Checking for new versions ]
echo.
echo ^<?xml version="1.0" encoding="UTF-8" standalone="yes"?^> > %~dp0addons.xml
echo ^<addons^> >> %~dp0addons.xml
for /f %%f in ('dir /b /a:d') do if exist %%f\addon.xml (
    del /q /s %%f\*.pyo >nul 2>&1>nul 2>&1
    del /q /s %%f\*.pyc >nul 2>&1
    del /q /s %%f\*.psd >nul 2>&1
	rd /S /Q %%f\.git >nul 2>&1
    set add=
    for /f "delims=" %%a in (%%f\addon.xml) do (
        set line=%%a
        if "!line:~0,6!"=="<addon" set add=1
        if not "!line!"=="!line:version=!" if "!add!"=="1" (
            set new=!line:version=ß!
            for /f "delims=ß tokens=2" %%n in ("!new!") do set new=%%n
            for /f "delims=^= " %%n in ("!new!") do set new=%%n
            set version=!new:^"=!
        )
        if "!line:~-1!"==">" set add=
        if not "!line:~0,5!"=="<?xml" echo %%a >> %~dp0addons.xml
    )
    if not exist %%f\%%f-!version!.zip (
        echo. 
		echo Found new version of %%f
		if exist "%%f\%%f*.zip" (
		echo Creating backup of existing old release
		IF not exist temp mkdir temp	
		IF not exist temp\%%f mkdir temp\%%f
		IF not exist temp\%%f\oldreleases mkdir temp\%%f\oldreleases
		move "%%f\%%f*.zip" temp\%%f\oldreleases >nul 2>&1
		)
        echo Creating %%f-!version!.zip
		%TOOLS%\7za a %%f\%%f-!version!.zip %%f -tzip -ax!%%f*.zip> nul
		echo. 
    ) else (
        echo. >nul 2>&1
		echo %%f-!version!.zip is up-to-date >nul 2>&1
    )
)
echo ^</addons^> >> %~dp0addons.xml
for /f "delims= " %%a in ('%TOOLS%\fciv -md5 %~dp0addons.xml') do echo %%a > %~dp0addons.xml.md5
echo.
echo.[ Index updated ]
echo.
echo.
TIMEOUT /T 2 /NOBREAK
goto :repoupdate

:repoupdate
echo.
echo.
echo.[ Commiting to repo ]
echo.
echo.
"%GIT%\git.exe" config --global push.default simple
"%GIT%\git.exe" add *
"%GIT%\git.exe" commit -a -m update
"%GIT%\git.exe" push
echo.
echo.
echo.[ Done. Exiting ]
echo.
echo.
PING 1.1.1.1 -n 1 -w 3000 >NUL
exit

:exitspot
echo.
echo.
echo.[ Exiting ]
echo.
echo.
PING 1.1.1.1 -n 1 -w 3000 >NUL
exit