@echo off

cd %~dp0source\golang

go run http2_socket_golang.go timer.go tools.go %1

pause
