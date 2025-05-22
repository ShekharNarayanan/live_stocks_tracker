@echo off
REM 1) go to your app folder
cd  "C:\Users\narayana\projects\personal\live-stocks-tracker"

REM 2) activate conda
call conda activate live-tracker
echo "conda env activated"

REM 3) run the streamlit app
call streamlit run app.py
pause



