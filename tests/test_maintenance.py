import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import main
import yaml
from main import detectar_modo_spec
from sdd_agent.crew import (
    ArquivoGerado,
    ProgramaGerado,
    RelatorioGerado,
    _codigo_com_linhas,
    _ler_documentos,
    _rodar_etapa,
    gerar_aplicacao_por_prompt,
)


ROOT = Path(__file__).resolve().parents[1]


class ModeDetectionTests(unittest.TestCase):
    def test_existing_specs_are_classified_correctly(self):
        self.assertEqual(detectar_modo_spec(ROOT / "specs/exemplo_tarefas.md"), "sdd")
        self.assertEqual(detectar_modo_spec(ROOT / "specs/linguagem_natural.md"), "natural")

    def test_content_detects_natural_prompt_with_generic_filename(self):
        with tempfile.TemporaryDirectory() as diretorio:
            spec = Path(diretorio) / "pedido.md"
            spec.write_text("# Pedido\nCrie uma lista de tarefas com filtros.", encoding="utf-8")
            self.assertEqual(detectar_modo_spec(spec), "natural")

    def test_cli_dispatches_auto_mode_without_local_import_regression(self):
        casos = (
            ("specs/exemplo_tarefas.md", "sdd"),
            ("specs/linguagem_natural.md", "natural"),
        )
        for caminho, modo_esperado in casos:
            with self.subTest(caminho=caminho):
                with (
                    patch.object(sys, "argv", ["main.py", caminho, "--modo", "auto", "--sem-abrir"]),
                    patch("sdd_agent.gerar_aplicacao", return_value=Path("/tmp/index.html")) as gerar_sdd,
                    patch(
                        "sdd_agent.gerar_aplicacao_por_prompt",
                        return_value=Path("/tmp/index.html"),
                    ) as gerar_natural,
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    self.assertEqual(main.main(), 0)

                if modo_esperado == "sdd":
                    gerar_sdd.assert_called_once()
                    gerar_natural.assert_not_called()
                else:
                    gerar_natural.assert_called_once()
                    gerar_sdd.assert_not_called()


class NaturalLanguageTests(unittest.TestCase):
    def test_empty_prompt_is_rejected_before_model_call(self):
        with patch("sdd_agent.crew._rodar_etapa") as rodar_etapa:
            with self.assertRaisesRegex(ValueError, "está vazio"):
                gerar_aplicacao_por_prompt("  \n", Path("saida"), verbose=False)
        rodar_etapa.assert_not_called()

    def test_markdown_file_is_read_for_generation_and_review(self):
        with tempfile.TemporaryDirectory() as diretorio:
            pedido = Path(diretorio) / "pedido.md"
            pedido.write_text("# Pedido\nCrie um contador simples.", encoding="utf-8")
            saida = Path(diretorio) / "saida"
            saida.mkdir()
            programa = ProgramaGerado(
                arquivos=[ArquivoGerado(caminho="index.html", conteudo="<main>0</main>")],
            )
            with (
                patch(
                    "sdd_agent.crew._rodar_etapa",
                    side_effect=[programa, "# Revisão\n\nAtendido."],
                ) as rodar_etapa,
                patch("sdd_agent.crew.gravar", return_value=saida / "index.html"),
            ):
                gerar_aplicacao_por_prompt(pedido, saida, verbose=False)

        chamadas = rodar_etapa.call_args_list
        prompt_geracao = chamadas[0].args[1]["PROMPT"]
        prompt_revisao = chamadas[1].args[1]["PROMPT"]
        self.assertIn("# Pedido", prompt_geracao)
        self.assertIn("Crie um contador simples.", prompt_revisao)

    def test_review_code_includes_exact_line_numbers(self):
        programa = ProgramaGerado(
            arquivos=[
                ArquivoGerado(
                    caminho="script.js",
                    conteudo="const valor = 1;\nconsole.log(valor);",
                )
            ]
        )
        codigo = _codigo_com_linhas(programa)
        self.assertIn("   1 | const valor = 1;", codigo)
        self.assertIn("   2 | console.log(valor);", codigo)


class AgentConfigurationTests(unittest.TestCase):
    def test_all_six_agents_are_referenced_by_pipeline_tasks(self):
        config_dir = ROOT / "sdd_agent/config"
        agents = yaml.safe_load((config_dir / "agents.yaml").read_text(encoding="utf-8"))
        tasks = yaml.safe_load((config_dir / "tasks.yaml").read_text(encoding="utf-8"))

        self.assertEqual(len(agents), 6)
        self.assertEqual({task["agent"] for task in tasks.values()}, set(agents))

    def test_comparison_task_returns_report_without_fake_program_files(self):
        resultado = SimpleNamespace(
            pydantic=RelatorioGerado(relatorio="# Comparação\n\nResumo."),
            raw="",
        )
        with (
            patch("sdd_agent.crew.criar_llm"),
            patch("sdd_agent.crew.Agent"),
            patch("sdd_agent.crew.Task") as tarefa,
            patch("sdd_agent.crew.Crew") as crew,
        ):
            crew.return_value.kickoff.return_value = resultado
            saida = _rodar_etapa("comparar", {}, "modelo-de-teste", verbose=False)

        self.assertEqual(saida, resultado.pydantic)
        self.assertIs(tarefa.call_args.kwargs["output_pydantic"], RelatorioGerado)


class DocumentReadingTests(unittest.TestCase):
    def test_truncated_files_are_reported(self):
        with tempfile.TemporaryDirectory() as diretorio:
            base = Path(diretorio)
            (base / "app.js").write_text("x" * 60_000, encoding="utf-8")

            documentos = _ler_documentos(base)

        self.assertIn("conteúdo truncado", documentos)
        self.assertIn("[... conteúdo truncado ...]", documentos)

    def test_unreadable_text_file_is_reported(self):
        with tempfile.TemporaryDirectory() as diretorio:
            base = Path(diretorio)
            (base / "app.js").write_bytes(b"\xff")
            (base / "index.html").write_text("<main>ok</main>", encoding="utf-8")

            documentos = _ler_documentos(base)

        self.assertIn("index.html", documentos)
        self.assertIn("codificação diferente de UTF-8", documentos)


if __name__ == "__main__":
    unittest.main()
