#!/usr/bin/env bash
# Cartaviva - instalación y arranque para macOS / Linux
set -e
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)
[ -z "$PY" ] && { echo "Instala Python 3.12+ desde https://www.python.org/downloads/"; exit 1; }
[ -d .venv ] || "$PY" -m venv .venv
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
python manage.py migrate
python manage.py cargar_demo
echo "Listo: abre http://127.0.0.1:8000  (CTRL+C para detener)"
python manage.py runserver
