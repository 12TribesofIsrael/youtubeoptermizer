@echo off
REM Task "BMB YouTube Competitor Tracker - weekly" runs this (Sundays 07:00). See scripts/competitor-tracker.py.
REM The notify.py fallback covers a crash before Python's own guard is loaded.
cd /d C:\Users\Claude\youtubeoptermizer
set PYTHONUTF8=1
C:\Python314\python.exe scripts\competitor-tracker.py 2> analytics\competitors\tracker.err
if errorlevel 1 C:\Python314\python.exe C:\Users\Claude\ecosystem\notify\notify.py --job "youtube competitor tracker" --summary "exit %errorlevel%" --detail-file analytics\competitors\tracker.err
