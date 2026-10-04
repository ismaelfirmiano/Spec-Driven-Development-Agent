#!/usr/bin/env bash
# Cria o ambiente virtual (.venv) e instala as dependências.
# Funciona em macOS e Linux. Uso: ./setup.sh
#
# O CrewAI exige Python >=3.10 e <3.14. O script procura um Python compatível
# já instalado; se não achar, tenta instalar o 3.13 (Homebrew no Mac, uv no Linux).
set -euo pipefail
cd "$(dirname "$0")"

versao_ok() {  # devolve 0 se o interpretador for 3.10 a 3.13
  "$1" -c 'import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] < (3,14) else 1)' 2>/dev/null
}

PY=""
for cand in python3.13 python3.12 python3.11 python3.10 python3 python; do
  if command -v "$cand" >/dev/null 2>&1 && versao_ok "$cand"; then
    PY="$(command -v "$cand")"; break
  fi
done

if [ -z "$PY" ]; then
  SO="$(uname -s)"
  if [ "$SO" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
    echo ">> Instalando Python 3.13 via Homebrew..."
    brew install python@3.13
    PY="$(brew --prefix python@3.13)/bin/python3.13"
  else
    # uv baixa um Python isolado, sem precisar de sudo nem mexer no sistema.
    if ! command -v uv >/dev/null 2>&1; then
      echo ">> Nenhum Python 3.10–3.13 encontrado. Instalando o uv (gerenciador de Python)..."
      curl -LsSf https://astral.sh/uv/install.sh | sh
      export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    fi
    if command -v uv >/dev/null 2>&1; then
      echo ">> Instalando Python 3.13 com uv..."
      uv python install 3.13
      PY="$(uv python find 3.13)"
    fi
  fi
fi

if [ -z "$PY" ] || ! versao_ok "$PY"; then
  cat >&2 <<'MSG'
ERRO: não encontrei Python entre 3.10 e 3.13 (o CrewAI não suporta 3.14).
Instale um e rode ./setup.sh de novo:
  Ubuntu/Debian:  sudo apt install python3.12 python3.12-venv
  Fedora:         sudo dnf install python3.12
  Arch:           sudo pacman -S python   (ou use o uv: https://docs.astral.sh/uv/)
  macOS:          brew install python@3.13
MSG
  exit 1
fi

echo ">> Usando $("$PY" --version) em $PY"
rm -rf .venv
if ! "$PY" -m venv .venv; then
  echo "ERRO: falhou ao criar o .venv. No Ubuntu/Debian instale o pacote venv:" >&2
  echo "  sudo apt install $(basename "$PY")-venv" >&2
  exit 1
fi
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

[ -f .env ] || { cp .env.example .env; echo ">> Criei .env — coloque sua GEMINI_API_KEY nele."; }

echo
echo "Pronto. Ative com:  source .venv/bin/activate"
echo "Rode com:          python main.py specs/exemplo_tarefas.md --abrir"
