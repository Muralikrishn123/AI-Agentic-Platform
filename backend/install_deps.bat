@echo off
echo Installing dependencies for Agentic AI Platform...
echo.
python -m pip install fastapi==0.109.0
python -m pip install uvicorn[standard]==0.27.0
python -m pip install pymongo==4.6.1
python -m pip install motor==3.3.2
python -m pip install pydantic==2.5.3
python -m pip install pydantic-settings==2.1.0
python -m pip install python-jose[cryptography]==3.3.0
python -m pip install passlib[bcrypt]==1.7.4
python -m pip install python-multipart==0.0.6
python -m pip install python-dotenv==1.0.0
python -m pip install google-generativeai==0.3.2
python -m pip install openai==1.10.0
python -m pip install httpx==0.26.0
echo.
echo ✅ Installation complete!
echo.
pause
