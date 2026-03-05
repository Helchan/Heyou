@echo off
chcp 65001 >nul
py main.py
if errorlevel 1 (
echo.
echo 程序异常退出，按任意键关闭...
pause >nul
)
