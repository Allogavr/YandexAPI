@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo Запуск тестов в 3 потока...
call .venv\Scripts\activate.bat
pytest -n 1 -v
pause