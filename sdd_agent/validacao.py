"""Validação automática do programa gerado (não depende do LLM).

O revisor é um modelo de linguagem e pode marcar um requisito como "atendido"
mesmo com o código quebrado. Esta etapa testa o programa de verdade:

1. Referências locais: todo <script src> e <link href> aponta para um arquivo
   que existe?
2. Navegador headless (Playwright, se instalado): abre o index.html, captura
   erros de JavaScript e de console, e envia cada formulário para ver se a
   página recarrega (sinal de que o JS não interceptou o envio).
3. Sem Playwright: checa a sintaxe dos .js e dos <script> internos com
   `node --check`, se o Node estiver instalado.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path


class _Referencias(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.locais: list[str] = []
        self.scripts_inline: list[str] = []
        self._em_script = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        alvo = a.get("src") if tag in ("script", "img") else a.get("href") if tag == "link" else None
        if alvo and not re.match(r"^(https?:|data:|//|#|mailto:)", alvo):
            self.locais.append(alvo.split("?")[0].split("#")[0])
        self._em_script = tag == "script" and not a.get("src")

    def handle_endtag(self, tag):
        if tag == "script":
            self._em_script = False

    def handle_data(self, data):
        if self._em_script and data.strip():
            self.scripts_inline.append(data)


def _checar_referencias(pasta: Path, html: Path) -> tuple[list[str], list[str]]:
    parser = _Referencias()
    parser.feed(html.read_text(encoding="utf-8", errors="replace"))
    problemas = [
        f"{html.name} referencia '{ref}', mas esse arquivo não foi gerado."
        for ref in parser.locais
        if not (html.parent / ref).exists()
    ]
    return problemas, parser.scripts_inline


def _checar_no_navegador(html: Path) -> list[str]:
    from playwright.sync_api import sync_playwright  # import opcional

    problemas: list[str] = []
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page()
        pagina.on("pageerror", lambda e: problemas.append(f"Erro de JavaScript: {e}"))
        pagina.on(
            "console",
            lambda m: problemas.append(f"Erro no console: {m.text}") if m.type == "error" else None,
        )
        pagina.goto(html.resolve().as_uri())
        pagina.wait_for_timeout(500)

        # Envia cada formulário com campos de texto preenchidos. Num app que
        # abre via file://, recarregar a página no envio é sempre um bug.
        total_forms = pagina.locator("form").count()
        for i in range(total_forms):
            form = pagina.locator("form").nth(i)
            campos = form.locator("input[type=text], input:not([type]), textarea")
            for j in range(campos.count()):
                campos.nth(j).fill("teste automático")
            pagina.evaluate("window.__sdd_sentinela = true")
            botao = form.locator("button[type=submit], button:not([type]), input[type=submit]")
            if botao.count():
                botao.first.click()
            else:
                form.evaluate("f => f.requestSubmit()")
            pagina.wait_for_timeout(300)
            if not pagina.evaluate("window.__sdd_sentinela === true"):
                problemas.append(
                    f"Enviar o formulário #{i + 1} recarrega a página: o JavaScript não "
                    "interceptou o 'submit' (falta preventDefault ou o script não carregou)."
                )
                pagina.goto(html.resolve().as_uri())
                pagina.wait_for_timeout(300)
        navegador.close()
    return list(dict.fromkeys(problemas))  # remove repetidos


def _checar_sintaxe_node(pasta: Path, scripts_inline: list[str]) -> list[str]:
    problemas: list[str] = []
    alvos = [(js.resolve(), js.relative_to(pasta).as_posix()) for js in pasta.rglob("*.js")]
    with tempfile.TemporaryDirectory() as tmp:
        for n, codigo in enumerate(scripts_inline, 1):
            arq = Path(tmp) / f"inline_{n}.js"
            arq.write_text(codigo, encoding="utf-8")
            alvos.append((arq, f"<script> interno #{n} do HTML"))
        for arq, nome in alvos:
            r = subprocess.run(["node", "--check", str(arq)], capture_output=True, text=True)
            if r.returncode != 0:
                detalhe = "\n".join(r.stderr.strip().splitlines()[:5]).replace(str(arq), nome)
                problemas.append(f"Erro de sintaxe em {nome}:\n{detalhe}")
    return problemas


def validar(pasta: Path, entrada: str = "index.html") -> tuple[list[str], str]:
    """Devolve (lista de problemas, descrição do método usado)."""
    html = pasta / entrada
    if not html.exists():
        return [f"O arquivo de entrada '{entrada}' não foi gerado."], "verificação de arquivos"

    problemas, scripts_inline = _checar_referencias(pasta, html)

    try:
        problemas += _checar_no_navegador(html)
        return problemas, "navegador headless (Playwright)"
    except Exception as erro:  # Playwright ausente ou navegador não instalado
        motivo = type(erro).__name__

    if shutil.which("node"):
        problemas += _checar_sintaxe_node(pasta, scripts_inline)
        return problemas, f"sintaxe via node --check (Playwright indisponível: {motivo})"

    return problemas, "apenas referências de arquivos (instale Playwright ou Node para validar o JS)"
