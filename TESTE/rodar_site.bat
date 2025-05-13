@echo off
cd /d %~dp0

REM Cria ambiente virtual se não existir
if not exist ".venv" (
    echo Criando ambiente virtual...
    python -m venv .venv
)

REM Instala dependências
echo Instalando dependências...
.venv\Scripts\python.exe -m pip install --quiet streamlit pandas openpyxl

REM Executa o site diretamente com o python da venv
echo Iniciando o site...
.venv\Scripts\python.exe -m streamlit run comissoes_app.py

pause
