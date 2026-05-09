@echo off
echo Starting Multi-Prompt Automation API...
pip install -r requirements.txt
uvicorn main:app --reload
pause
