@echo off
REM 1) go to your app folder
cd  "C:\Users\narayana\projects\personal\live_stocks_tracker\src"

REM 2) activate conda
call conda activate live-tracker

REM 3) run the streamlit app
call streamlit run live_stocks_tracker\app.py
pause



