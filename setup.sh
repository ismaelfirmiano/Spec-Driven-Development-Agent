#!/usr/bin/env bash
# Recria o ambiente virtual com Python 3.13 e instala as dependências.
# Uso: ./setup.sh
set -euo pipefail
cd "$(dirname "$0")"

PY=""
for cand in python3.13 python3.12 python3.11; do
  if command -v "$cand" >/dev/null 2>&1; then PY="$cand"; break; fi
done

if [ -z "$PY" ]; then
  if command -v brew >/dev/null 2>&1; then
    echo ">> Instalando Python 3.13 via Homebrew (CrewAI não suporta 3.14)..."
    brew install python@3.13
    PY="$(brew --prefix python@3.13)/bin/python3.13"
  else
    echo "ERRO: instale o Python 3.13 (CrewAI exige >=3.10 e <3.14)." >&2
    exit 1
  fi
fi

echo ">> Usando $($PY --version)"
rm -rf .venv
"$PY" -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

[ -f .env ] || { cp .env.example .env; echo ">> Criado .env — coloque sua GEMINI_API_KEY nele."; }

echo
echo "Pronto. Ative com:  source .venv/bin/activate"
echo "Rode com:          python main.py specs/exemplo_tarefas.md --abrir"
