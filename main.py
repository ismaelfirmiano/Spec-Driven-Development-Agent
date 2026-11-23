"""Agente de IA para Spec-Driven Development.

Uso:
    python main.py specs/exemplo_tarefas.md            # gera em output/exemplo_tarefas/
    python main.py specs/minha_spec.md --abrir         # gera e abre no navegador
    python main.py specs/minha_spec.md -o saida/ -q    # pasta própria, sem logs
    python main.py --spec specs/minha_spec.md --modo sdd
    python main.py --spec specs/linguagem_natural.md --modo natural --abrir
    python main.py --prompt "Crie um gerenciador de tarefas web" # cria pela linguagem natural
    python main.py --experimento specs/todomvc_sdd.md specs/todomvc_natural.md
                                                       # gera SDD + natural e compara às cegas
    python main.py --comparar output/x natural_language/y --referencia specs/x.md
    python main.py --avaliar                             # avalia e corrige a geração mais recente
    python main.py --avaliar output/exemplo_tarefas      # avalia uma pasta específica
    python main.py --modelos                           # lista modelos Gemini disponíveis
"""

import argparse
import re
import sys
import webbrowser
from pathlib import Path

from dotenv import load_dotenv


def detectar_modo_spec(arquivo_spec: Path) -> str:
    """Detecta SDD ou linguagem natural pelo conteúdo e pelo nome do arquivo."""
    nome = arquivo_spec.stem.lower()
    if "linguagem_natural" in nome or nome.startswith("natural"):
        return "natural"

    texto = arquivo_spec.read_text(encoding="utf-8")
    texto_limpo = texto.lower()

    marcadores_sdd = (
        "(sdd)",
        "spec-driven",
        "requisitos funcionais",
        "requisitos não-funcionais",
        "regras de negócio",
        "critérios de aceitação",
        "fora do escopo",
        "matriz de rastreabilidade",
        "checklist de entrega",
        "modelo de dados",
        "arquitetura",
        "especificação técnica",
    )
    marcadores_natural = (
        "pedido em linguagem natural",
        "crie ",
        "gere ",
        "faça ",
        "desenvolva uma ",
        "desenvolva o ",
        "construa ",
        "implemente ",
    )

    pontos_sdd = sum(2 for marcador in marcadores_sdd if marcador in texto_limpo)
    pontos_sdd += len(re.findall(r"\brf[- ]?\d+\b|\brnf[- ]?\d+\b", texto_limpo)) * 2
    pontos_natural = sum(2 for marcador in marcadores_natural if marcador in texto_limpo)

    if "sdd" in nome or "spec" in nome:
        pontos_sdd += 1

    return "natural" if pontos_natural > pontos_sdd else "sdd"


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Gera aplicações SDD ou por linguagem natural.",
        epilog=(
            "Uso rápido: python main.py specs/exemplo_tarefas.md --abrir | "
            "python main.py --prompt \"Crie uma lista de tarefas\" --abrir"
        ),
    )
    parser.add_argument("spec", type=Path, nargs="?", help="Arquivo de especificação (.md ou .txt)")
    parser.add_argument("--spec", dest="spec_opcao", type=Path, help="Arquivo de especificação (forma explícita)")
    parser.add_argument("-o", "--saida", type=Path, help="Pasta de saída personalizada")
    parser.add_argument("--abrir", action="store_true", help="Abre o resultado no navegador ao final (padrão)")
    parser.add_argument("--sem-abrir", action="store_true", help="Não abre o navegador ao concluir")
    parser.add_argument("-q", "--quieto", action="store_true", help="Oculta o log detalhado dos agentes")
    parser.add_argument("-m", "--modelo", help="Modelo a usar nesta execução (ex.: gemini/gemini-3.8-flash)")
    parser.add_argument("--prompt", help="Cria o programa a partir de um pedido em linguagem natural")
    parser.add_argument("--modo", choices=("sdd", "natural", "auto"), default="auto", help="Tipo de execução ao usar --spec ou spec posicional")
    parser.add_argument("--avaliar", nargs="?", const="auto", metavar="CAMINHO", help="Avalia e corrige o último código SDD/natural ou uma pasta/arquivo informado")
    parser.add_argument("--comparar", nargs=2, metavar=("SDD", "NATURAL"), help="Compara às cegas uma geração SDD com uma em linguagem natural")
    parser.add_argument("--referencia", type=Path, help="Especificação usada como gabarito no --comparar (padrão: ESPECIFICACAO.md da pasta SDD)")
    parser.add_argument("--experimento", nargs=2, type=Path, metavar=("SPEC_SDD", "PEDIDO_NATURAL"), help="Gera as duas versões nas mesmas condições e compara às cegas")
    parser.add_argument("--revisar", action="store_true", help="Liga a revisão automática (aplicada igualmente a SDD e natural)")
    parser.add_argument("--tipo-avaliacao", choices=("auto", "sdd", "natural"), default="auto", help="Tipo da avaliação: automático, SDD ou linguagem natural")
    parser.add_argument("--modelos", action="store_true", help="Lista os modelos Gemini disponíveis para sua chave")
    args = parser.parse_args()

    if args.modelos:
        return listar_modelos()

    modos = sum(bool(valor) for valor in (args.prompt, args.avaliar, args.comparar, args.experimento))
    if modos > 1:
        parser.error("use somente um modo por vez: --prompt, --avaliar, --comparar ou --experimento")

    # Import adiado: deixa --help rápido e dá erro claro se faltar dependência.
    from sdd_agent import (
        avaliar_codigo,
        comparar_codigo,
        executar_experimento,
        gerar_aplicacao,
        gerar_aplicacao_por_prompt,
    )

    if args.experimento:
        spec, pedido = args.experimento
        for caminho in (spec, pedido):
            if not caminho.is_file():
                print(f"Arquivo não encontrado: {caminho}", file=sys.stderr)
                return 1
        try:
            relatorio = executar_experimento(
                spec, pedido, args.saida, verbose=not args.quieto,
                modelo=args.modelo, revisar=args.revisar,
            )
        except (RuntimeError, ValueError, FileNotFoundError) as erro:
            print(f"Erro no experimento: {erro}", file=sys.stderr)
            return 1
        print(f"\nRelatório comparativo: {relatorio.resolve()}")
        return 0

    if args.comparar:
        try:
            relatorio = comparar_codigo(
                Path(args.comparar[0]),
                Path(args.comparar[1]),
                verbose=not args.quieto,
                modelo=args.modelo,
                referencia=args.referencia,
            )
        except (RuntimeError, ValueError, FileNotFoundError) as erro:
            print(f"Erro na comparação: {erro}", file=sys.stderr)
            return 1
        print(f"\nComparação gravada em: {relatorio.resolve()}")
        return 0

    if args.avaliar:
        try:
            relatorio = avaliar_codigo(
                None if args.avaliar == "auto" else Path(args.avaliar),
                verbose=not args.quieto,
                modelo=args.modelo,
                tipo=args.tipo_avaliacao,
            )
        except (RuntimeError, ValueError, FileNotFoundError) as erro:
            print(f"Erro na avaliação: {erro}", file=sys.stderr)
            return 1
        print(f"\nAvaliação gravada em: {relatorio.resolve()}")
        return 0

    if args.prompt:
        if args.spec or args.spec_opcao:
            parser.error("não use spec e --prompt ao mesmo tempo")
        slug = re.sub(r"[^a-z0-9]+", "_", args.prompt.lower()).strip("_")[:50] or "prompt"
        pasta = args.saida or Path("natural_language") / slug
        try:
            entrada = gerar_aplicacao_por_prompt(
                args.prompt, pasta, verbose=not args.quieto, modelo=args.modelo,
                revisar=args.revisar,
            )
        except (RuntimeError, ValueError, FileNotFoundError) as erro:
            print(f"Erro na geração por linguagem natural: {erro}", file=sys.stderr)
            return 1
        print(f"\nPrograma gerado em: {pasta.resolve()}")
        print(f"Abra no navegador:  {entrada.as_uri()}")
        if not args.sem_abrir:
            webbrowser.open(entrada.as_uri())
        return 0

    arquivo_spec = args.spec_opcao or args.spec
    if args.spec_opcao and args.spec:
        parser.error("use o caminho posicional ou --spec, não os dois")
    if arquivo_spec is None:
        parser.error("informe o arquivo de especificação ou use --prompt")
    if not arquivo_spec.is_file():
        print(f"Especificação não encontrada: {arquivo_spec}", file=sys.stderr)
        return 1

    slug = re.sub(r"[^a-z0-9]+", "_", arquivo_spec.stem.lower()).strip("_") or "projeto"
    modo = args.modo
    if modo == "auto":
        modo = detectar_modo_spec(arquivo_spec)
        print(f"Modo detectado automaticamente: {modo.upper()}")

    if modo == "natural":
        pasta = args.saida or Path("natural_language") / slug
        try:
            entrada = gerar_aplicacao_por_prompt(
                arquivo_spec,
                pasta,
                verbose=not args.quieto,
                modelo=args.modelo,
                revisar=args.revisar,
            )
        except (RuntimeError, ValueError, FileNotFoundError) as erro:
            print(f"Erro na geração natural: {erro}", file=sys.stderr)
            return 1
        print(f"\nPrograma gerado em: {pasta.resolve()}")
        print(f"Abra no navegador:  {entrada.as_uri()}")
        if not args.sem_abrir:
            webbrowser.open(entrada.as_uri())
        return 0

    pasta = args.saida or Path("output") / arquivo_spec.stem
    try:
        entrada = gerar_aplicacao(
            arquivo_spec,
            pasta,
            verbose=not args.quieto,
            modelo=args.modelo,
            revisar=args.revisar,
        )
    except (RuntimeError, ValueError, FileNotFoundError) as erro:
        print(f"Erro na geração SDD: {erro}", file=sys.stderr)
        return 1

    print(f"\nPrograma gerado em: {pasta.resolve()}")
    print(f"Abra no navegador:  {entrada.as_uri()}")
    if not args.sem_abrir:
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
