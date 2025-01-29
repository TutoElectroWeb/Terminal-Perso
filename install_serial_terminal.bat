REM filepath: /C:/Users/weedm/Desktop/Terminal Perso/install_and_run.bat
@echo off
REM Vérifier si Python est installé
python --version
IF %ERRORLEVEL% NEQ 0 (
    echo Python n'est pas installé. Téléchargement et installation de la dernière version de Python...
    REM Télécharger le programme d'installation de Python
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe -OutFile python_installer.exe"
    REM Installer Python silencieusement
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    REM Supprimer le programme d'installation
    del python_installer.exe
    REM Vérifier à nouveau si Python est installé
    python --version
    IF %ERRORLEVEL% NEQ 0 (
        echo L'installation de Python a échoué. Veuillez installer Python manuellement depuis https://www.python.org/downloads/
        exit /b 1
    )
)

REM Vérifier si pip est installé
pip --version
IF %ERRORLEVEL% NEQ 0 (
    echo pip n'est pas installé. Téléchargement et installation de pip...
    REM Télécharger get-pip.py
    powershell -Command "Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py"
    REM Installer pip
    python get-pip.py
    REM Supprimer get-pip.py
    del get-pip.py
    REM Vérifier à nouveau si pip est installé
    pip --version
    IF %ERRORLEVEL% NEQ 0 (
        echo L'installation de pip a échoué. Veuillez installer pip manuellement depuis https://pip.pypa.io/en/stable/installation/
        exit /b 1
    )
)

REM Installer les dépendances
pip install PyQt5 pyserial

REM Exécuter le script en arrière-plan
start pythonw serial_terminal.pyw

exit