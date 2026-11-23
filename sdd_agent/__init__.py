"""Agente de IA para Spec-Driven Development (CrewAI + Gemini)."""

from .crew import (
    avaliar_codigo,
    comparar_codigo,
    executar_experimento,
    gerar_aplicacao,
    gerar_aplicacao_por_prompt,
)

__all__ = [
    "avaliar_codigo",
    "comparar_codigo",
    "executar_experimento",
    "gerar_aplicacao",
    "gerar_aplicacao_por_prompt",
]
