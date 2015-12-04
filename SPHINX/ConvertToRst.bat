@echo off
for /r %%i in (*.docx) do (
 pandoc -s %%~ni.docx -t markdown -o %%~ni.md
 DEL %%~ni.rst
 REN  %%~ni.md %%~ni.rst
 DEL %%~ni.docx %%~ni.md
 )