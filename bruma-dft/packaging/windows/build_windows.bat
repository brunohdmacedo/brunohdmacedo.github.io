@echo off
REM Compila o Bruma para Windows nesta máquina (Python 3.10+ instalado).
REM Resultado: dist\Bruma.exe (janela), dist\bruma-cli.exe (linha de comando)
REM e, se o Inno Setup 6 estiver instalado, dist\Bruma-Setup-1.0.0.exe.
cd /d "%~dp0\..\.."
python -m pip install --upgrade pip
python -m pip install numpy matplotlib pillow pyinstaller
REM foto do autor (a mesma do Lattes e do site); se falhar, o programa mostra as iniciais
powershell -Command "try { Invoke-WebRequest -UseBasicParsing -Uri 'https://wwws.cnpq.br/cvlattesweb/pkg_util_img.show_foto?v_cod=K4494050P3' -OutFile 'assets\autor.jpg' } catch { Write-Host 'Foto nao baixada' }"
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Bruma --icon assets\bruma.ico --add-data "assets;assets" --hidden-import PIL._tkinter_finder --exclude-module scipy --exclude-module pandas --exclude-module IPython --exclude-module PyQt5 --exclude-module PyQt6 --exclude-module PySide2 --exclude-module PySide6 --exclude-module notebook --exclude-module jedi --exclude-module sympy bruma_gui.py
python -m PyInstaller --noconfirm --clean --onefile --console --name bruma-cli --icon assets\bruma.ico --exclude-module scipy --exclude-module pandas --exclude-module IPython --exclude-module PyQt5 --exclude-module PyQt6 --exclude-module PySide2 --exclude-module PySide6 --exclude-module notebook --exclude-module jedi --exclude-module sympy --exclude-module tkinter bruma.py
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
  "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" packaging\windows\bruma.iss
) else (
  echo Inno Setup 6 nao encontrado: os executaveis estao em dist\, sem instalador.
)
pause
