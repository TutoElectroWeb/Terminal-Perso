@echo off
REM Désactive l'affichage des commandes dans la console

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
IF %ERRORLEVEL% NEQ 0 (
    echo L'installation des dépendances a échoué. Masquage du fichier serial_terminal.pyw...
    ren serial_terminal.pyw serial_terminal.pyw.hidden
    exit /b 1
)

REM Décacher le fichier serial_terminal.txt
attrib -h serial_terminal.txt

REM Renommer le fichier serial_terminal.txt en serial_terminal.pyw
ren serial_terminal.txt serial_terminal.pyw

REM Supprimer le fichier README.md s'il existe
IF EXIST README.md (
    del README.md
)

REM Supprimer ce fichier batch
del "%~f0"

endlocal
REM Termine le bloc de localisation des variables et restaure les paramètres d'environnement précédents

exit
REM Quitte le script batch