"""Compara um agente SDD com um agente de linguagem natural.

Uso:
    python main.py                  # usa entrada.md (SDD) e entrada.txt (natural)
    python main.py specs/taskflow   # usa specs/taskflow.md e specs/taskflow.txt
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Compara SDD com linguagem natural.")
    parser.add_argument("entrada", nargs="?", default="entrada",
                        help="nome dos arquivos de entrada, sem extensão (padrão: entrada)")
    parser.add_argument("-o", "--saida", type=Path, help="pasta onde salvar o resultado")
    parser.add_argument("-m", "--modelo", help="modelo a usar, ex.: gemini/gemini-3.5-flash")
    args = parser.parse_args()

    base = Path(args.entrada).with_suffix("")
    arquivo_md = base.with_suffix(".md")
    arquivo_txt = base.with_suffix(".txt")
    for arquivo in (arquivo_md, arquivo_txt):
        if not arquivo.is_file():
            print(f"Arquivo não encontrado: {arquivo}", file=sys.stderr)
            return 1

    data = datetime.now().strftime("%Y%m%d_%H%M%S")
    pasta = args.saida or Path("resultados") / f"{base.name}_{data}"

    from agentes import rodar_experimento

    try:
        relatorio = rodar_experimento(arquivo_md, arquivo_txt, pasta, args.modelo)
    except RuntimeError as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1

    print(f"\nProgramas gerados em: {pasta}/sdd e {pasta}/natural")
    print(f"Relatório: {relatorio}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
