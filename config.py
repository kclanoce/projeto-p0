"""Carregamento e validação da configuração (arquivo .env e variáveis de ambiente)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from erros import ErroConfiguracao, ErroCredencial

CHAVE_EXEMPLO = "coloque_sua_chave_aqui"
MODELO_EXEMPLO = "id-do-modelo"
TIMEOUT_PADRAO_S = 30
MAX_TOKENS_PADRAO = 2048
TEMPERATURA_PADRAO = 0.2
NIVEL_LOG_PADRAO = "INFO"
ARQUIVO_LOG_PADRAO = "app.log"
NIVEIS_LOG = ("DEBUG", "INFO", "WARNING", "ERROR")


@dataclass(frozen=True)
class Configuracao:
    api_key: str
    modelo: str
    timeout_s: int
    max_output_tokens: int = MAX_TOKENS_PADRAO
    temperatura: float = TEMPERATURA_PADRAO
    nivel_log: str = NIVEL_LOG_PADRAO
    arquivo_log: str = ARQUIVO_LOG_PADRAO

    def __repr__(self) -> str:
        # Evita que a chave apareça sem querer em prints ou logs.
        return (
            f"Configuracao(api_key='***', modelo={self.modelo!r}, timeout_s={self.timeout_s}, "
            f"max_output_tokens={self.max_output_tokens}, temperatura={self.temperatura}, "
            f"nivel_log={self.nivel_log!r}, arquivo_log={self.arquivo_log!r})"
        )


def _ler(nome: str, padrao) -> str:
    return (os.getenv(nome) or str(padrao)).strip()


def _inteiro_positivo(nome: str, padrao: int) -> int:
    try:
        valor = int(_ler(nome, padrao))
    except ValueError:
        valor = 0
    if valor <= 0:
        raise ErroConfiguracao(f"{nome} deve ser um número inteiro positivo.")
    return valor


def _temperatura() -> float:
    texto = _ler("GEMINI_TEMPERATURE", TEMPERATURA_PADRAO).replace(",", ".")
    try:
        valor = float(texto)
    except ValueError:
        valor = -1.0
    if not 0.0 <= valor <= 2.0:
        raise ErroConfiguracao("GEMINI_TEMPERATURE deve ser um número entre 0 e 2.")
    return valor


def carregar_configuracao(ler_dotenv: bool = True) -> Configuracao:
    """Lê e valida a configuração. Levanta erro claro se algo faltar."""
    if ler_dotenv:
        load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == CHAVE_EXEMPLO:
        raise ErroCredencial(
            "A chave de API não foi configurada. Copie o arquivo .env.example para .env "
            "e preencha GEMINI_API_KEY com a sua chave."
        )

    modelo = os.getenv("GEMINI_MODEL", "").strip()
    if not modelo or modelo == MODELO_EXEMPLO:
        raise ErroConfiguracao(
            "O modelo não foi configurado. Preencha GEMINI_MODEL no arquivo .env com o ID do modelo."
        )

    nivel_log = _ler("LOG_LEVEL", NIVEL_LOG_PADRAO).upper()
    if nivel_log not in NIVEIS_LOG:
        raise ErroConfiguracao(f"LOG_LEVEL deve ser um destes valores: {', '.join(NIVEIS_LOG)}.")

    return Configuracao(
        api_key=api_key,
        modelo=modelo,
        timeout_s=_inteiro_positivo("GEMINI_TIMEOUT", TIMEOUT_PADRAO_S),
        max_output_tokens=_inteiro_positivo("GEMINI_MAX_OUTPUT_TOKENS", MAX_TOKENS_PADRAO),
        temperatura=_temperatura(),
        nivel_log=nivel_log,
        arquivo_log=_ler("LOG_FILE", ARQUIVO_LOG_PADRAO),
    )