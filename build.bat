@echo off
REM 删除旧的文件夹
rmdir /s /q dist
rmdir /s /q build

REM 创建新的文件夹
mkdir dist
mkdir build

REM 打包应用程序
pyinstaller -F -w -n 163musicdownload .\src\main.py 

pause 