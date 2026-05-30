@echo off
echo Instalando as dependencias necessarias...
pip install -r requirements.txt

echo.
echo Iniciando o Dashboard...
python main.py

pause
