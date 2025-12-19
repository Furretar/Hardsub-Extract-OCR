@echo off
for %%f in (*.idx) do java -jar BDSup2Sub.jar "%%f" -o "%%~nf.sup"
pause
