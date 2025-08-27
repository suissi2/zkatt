@echo off
echo ========================================
echo   Lancement de l'Application ZKAtt
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo Erreur: Python n'est pas installé ou n'est pas dans le PATH
    echo Veuillez installer Python 3.8+ depuis https://python.org
    pause
    exit /b 1
)

REM Vérifier et installer les dépendances
echo Vérification des dépendances...
pip install -r requirements.txt

REM Lancer l'application
echo.
echo Lancement de l'application...
python main.py

REM Pause à la fin pour voir les éventuels messages d'erreur
pause
