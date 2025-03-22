@echo off
title Proxy Checker
chcp 65001 >nul
cls

echo Проверка зависимостей...
python -m pip install --upgrade pip >nul 2>&1
pip install requests colorama pyfiglet >nul 2>&1

echo Запуск Proxy Fucker...
python check.py
pause
