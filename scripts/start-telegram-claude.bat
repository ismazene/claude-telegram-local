@echo off
title Claude Telegram
cd /d "%USERPROFILE%"
:loop
call "%APPDATA%\npm\claude.cmd" --channels plugin:telegram@claude-plugins-official
timeout /t 10
goto loop
