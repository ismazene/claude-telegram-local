@echo off
title Claude Telegram
cd /d "%USERPROFILE%"
start "" /b pythonw -m tgmedia serve
:loop
call "%APPDATA%\npm\claude.cmd" --channels plugin:telegram@claude-plugins-official
timeout /t 10
goto loop
