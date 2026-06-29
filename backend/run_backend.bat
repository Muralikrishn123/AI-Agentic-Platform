@echo off
set PYTHONIOENCODING=utf-8
python -m uvicorn app.main:app --port 8001
