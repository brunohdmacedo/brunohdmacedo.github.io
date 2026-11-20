@echo off
REM Compila o BrUMaRe para Windows nesta máquina (Python 3.10+ instalado).
REM Resultado: dist\BrUMaRe.exe (janela), dist\brumare.exe (linha de comando)
REM e, se o Inno Setup 6 estiver instalado, dist\BrUMaRe-Setup-1.0.0.exe.
cd /d "%~dp0\..\.."
python -m pip install --upgrade pip
python -m pip install numpy matplotlib pillow pywebview pyinstaller
REM interface offline: copia do site em brumare_app\web
python tools\montar_app.py
REM foto do autor (a mesma do Lattes e do site); se falhar, o programa mostra as iniciais
powershell -Command "try { Invoke-WebRequest -UseBasicParsing -Uri 'https://wwws.cnpq.br/cvlattesweb/pkg_util_img.show_foto?v_cod=K4494050P3' -OutFile 'assets\autor.jpg' } catch { Write-Host 'Foto nao baixada' }"
python -m PyInstaller --noconfirm --clean --onefile --windowed --name BrUMaRe --icon assets\brumare.ico --add-data "brumare_app\web;brumare_app\web" --add-data "assets;assets" --collect-all webview --hidden-import clr --exclude-module scipy --exclude-module pandas --exclude-module IPython --exclude-module PyQt5 --exclude-module PyQt6 --exclude-module PySide2 --exclude-module PySide6 --exclude-module notebook --exclude-module jedi --exclude-module sympy brumare_gui.py
python -m PyInstaller --noconfirm --clean --onefile --console --name brumare --icon assets\brumare.ico --exclude-module scipy --exclude-module pandas --exclude-module IPython --exclude-module PyQt5 --exclude-module PyQt6 --exclude-module PySide2 --exclude-module PySide6 --exclude-module notebook --exclude-module jedi --exclude-module sympy --exclude-module tkinter brumare.py
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
  "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" packaging\windows\brumare.iss
) else (
  echo Inno Setup 6 nao encontrado: os executaveis estao em dist\, sem instalador.
)
pause
