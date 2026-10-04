"""Agente de IA para Spec-Driven Development.

Uso:
    python main.py specs/exemplo_tarefas.md            # gera em output/exemplo_tarefas/
    python main.py specs/minha_spec.md --abrir         # gera e abre no navegador
    python main.py specs/minha_spec.md -o saida/ -q    # pasta própria, sem logs
    python main.py --modelos                           # lista modelos Gemini disponíveis
"""

import argparse
import sys
import webbrowser
from pathlib import Path

from dotenv import load_dotenv


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Gera um programa web a partir de uma especificação.")
    parser.add_argument("spec", type=Path, nargs="?", help="Arquivo de especificação (.md ou .txt)")
    parser.add_argument("-o", "--saida", type=Path, help="Pasta de saída (padrão: output/<nome-da-spec>)")
    parser.add_argument("--abrir", action="store_true", help="Abre o resultado no navegador ao final")
    parser.add_argument("-q", "--quieto", action="store_true", help="Oculta o log detalhado dos agentes")
    parser.add_argument("-m", "--modelo", help="Modelo a usar nesta execução (ex.: gemini/gemini-3.8-flash)")
    parser.add_argument("--modelos", action="store_true", help="Lista os modelos Gemini disponíveis para sua chave")
    args = parser.parse_args()

    if args.modelos:
        return listar_modelos()
    if args.spec is None:
        parser.error("informe o arquivo de especificação")
    if not args.spec.is_file():
        print(f"Especificação não encontrada: {args.spec}", file=sys.stderr)
        return 1

    # Import adiado: deixa --help rápido e dá erro claro se faltar dependência.
    from sdd_agent import gerar_aplicacao

    pasta = args.saida or Path("output") / args.spec.stem
    entrada = gerar_aplicacao(args.spec, pasta, verbose=not args.quieto, modelo=args.modelo)

    print(f"\nPrograma gerado em: {pasta.resolve()}")
    print(f"Abra no navegador:  {entrada.as_uri()}")
    if args.abrir:
        webbrowser.open(entrada.as_uri())
    return 0


def listar_modelos() -> int:
    """Mostra os modelos que a chave atual pode usar para gerar texto."""
    from google import genai

    cliente = genai.Client()  # lê GEMINI_API_KEY / GOOGLE_API_KEY do ambiente
    print("Modelos disponíveis (use no .env como SDD_MODEL=gemini/<nome>):\n")
    for m in cliente.models.list():
        acoes = getattr(m, "supported_actions", None) or []
        if "generateContent" in acoes:
            print("  " + m.name.removeprefix("models/"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
