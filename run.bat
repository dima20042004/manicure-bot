@echo off
chcp 65001 >nul
echo ======================================
echo Установка ВСЕХ необходимых библиотек...
echo ======================================
pip install importlib_metadata tokenizers typer accelerate safetensors regex
pip install diffusers==0.26.0 transformers==4.35.0

echo.
echo ======================================
echo Запуск бота...
echo ======================================
python bot.py
pause