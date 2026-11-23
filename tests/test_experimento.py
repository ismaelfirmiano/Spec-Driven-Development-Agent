import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from agentes.crew import (
    Arquivo,
    Comparacao,
    Execucao,
    Programa,
    Requisito,
    cobertura,
    esconder_ids,
    extrair_requisitos,
    rodar_experimento,
    salvar_programa,
    verificar_programa,
)

RAIZ = Path(__file__).resolve().parents[1]


def execucao(saida, tokens):
    return Execucao(saida, segundos=1.0, tokens_entrada=tokens, tokens_saida=tokens,
                    tokens_total=2 * tokens, tentativas=1)


class ConfiguracaoTests(unittest.TestCase):
    def test_tres_agentes(self):
        agentes = yaml.safe_load((RAIZ / "agentes/config/agents.yaml").read_text(encoding="utf-8"))
        self.assertEqual(set(agentes), {"agente_sdd", "agente_natural", "comparador"})

    def test_regras_tecnicas_iguais_para_os_dois_desenvolvedores(self):
        tarefas = yaml.safe_load((RAIZ / "agentes/config/tasks.yaml").read_text(encoding="utf-8"))

        def regras(nome):
            texto = tarefas[nome]["description"]
            return texto[texto.index("Regras técnicas"):texto.index("=====")]

        self.assertEqual(regras("desenvolver_sdd"), regras("desenvolver_natural"))

    def test_entradas_existem(self):
        self.assertTrue((RAIZ / "entrada.md").is_file())
        self.assertTrue((RAIZ / "entrada.txt").is_file())

    def test_extrai_requisitos_sem_objetivos_e_criterios(self):
        texto = "- **OBJ-01** objetivo\n- **FR-001** um\n### RF-002 — dois\nRN-01\nCA-001\n| FR-001 | tabela |"
        self.assertEqual(extrair_requisitos(texto), ["FR-001", "RF-002", "RN-01"])
        self.assertEqual(len(extrair_requisitos((RAIZ / "specs/conduit.md").read_text(encoding="utf-8"))), 87)

    def test_todo_caso_tem_md_e_txt(self):
        for md in (RAIZ / "specs").glob("*.md"):
            with self.subTest(caso=md.stem):
                self.assertTrue(md.with_suffix(".txt").is_file())


class ExperimentoTests(unittest.TestCase):
    def test_cobertura(self):
        reqs = [
            Requisito(id="1", descricao="", versao_a="atendido", evidencia_a="", versao_b="parcial", evidencia_b=""),
            Requisito(id="2", descricao="", versao_a="não atendido", evidencia_a="", versao_b="parcial", evidencia_b=""),
        ]
        self.assertEqual(cobertura(reqs, "versao_a"), 50.0)
        self.assertEqual(cobertura(reqs, "versao_b"), 50.0)

    def test_programa_cortado_e_recusado(self):
        cortado = Programa(arquivos=[Arquivo(caminho="index.html", conteudo="<html><body><a class=")])
        with self.assertRaises(ValueError):
            verificar_programa(cortado)
        sem_js = Programa(arquivos=[Arquivo(caminho="index.html",
                                            conteudo='<html><script src="app.js"></script></html>')])
        with self.assertRaises(ValueError):
            verificar_programa(sem_js)
        completo = Programa(arquivos=[
            Arquivo(caminho="index.html", conteudo='<html><script src="./js/app.js"></script></html>'),
            Arquivo(caminho="js/app.js", conteudo="1;"),
        ])
        verificar_programa(completo)

    def test_comentarios_com_ids_sao_escondidos(self):
        self.assertEqual(esconder_ids("// RF-28: paginação"), "")
        self.assertEqual(esconder_ids("const n = 10; // RF-28"), "const n = 10;")
        self.assertEqual(esconder_ids("<!-- FR-001 -->"), "")
        self.assertEqual(esconder_ids("const id = 'AB-12';"), "const id = 'AB-12';")
        self.assertEqual(esconder_ids("let x = 1; // comum"), "let x = 1; // comum")

    def test_caminho_fora_da_pasta_e_rejeitado(self):
        with tempfile.TemporaryDirectory() as pasta:
            programa = Programa(arquivos=[Arquivo(caminho="../fora.html", conteudo="x")])
            with self.assertRaises(ValueError):
                salvar_programa(programa, Path(pasta))

    def test_fluxo_completo_sem_revisao(self):
        programa_sdd = Programa(arquivos=[Arquivo(caminho="index.html", conteudo="<p>sdd</p>")])
        programa_natural = Programa(arquivos=[Arquivo(caminho="index.html", conteudo="<p>natural</p>")])
        comparacao = Comparacao(
            requisitos=[Requisito(id="RF-01", descricao="d", versao_a="atendido", evidencia_a="a",
                                  versao_b="não atendido", evidencia_b="b")],
            conclusao="ok",
        )
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            (pasta / "e.md").write_text("spec", encoding="utf-8")
            (pasta / "e.txt").write_text("pedido", encoding="utf-8")
            respostas = [execucao(programa_sdd, 100), execucao(programa_natural, 50), execucao(comparacao, 10)]
            with patch("agentes.crew.executar", side_effect=respostas) as executar:
                relatorio = rodar_experimento(pasta / "e.md", pasta / "e.txt", pasta / "saida",
                                              modelo="teste", seed=0)

            chamadas = [c.args[0] for c in executar.call_args_list]
            self.assertEqual(chamadas, ["desenvolver_sdd", "desenvolver_natural", "comparar"])
            valores = executar.call_args_list[2].args[1]
            self.assertNotIn("sdd", (valores["VERSAO_A"] + valores["VERSAO_B"]).replace("<p>sdd</p>", ""))
            texto = relatorio.read_text(encoding="utf-8")
            self.assertIn("| Tokens totais | 200 | 100 |", texto)
            self.assertIn("Cobertura dos requisitos", texto)


if __name__ == "__main__":
    unittest.main()
