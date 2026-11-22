"""Carregamento e validação da configuração (arquivo .env e variáveis de ambiente)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from erros import ErroConfiguracao, ErroCredencial

CHAVE_EXEMPLO = "coloque_sua_chave_aqui"
MODELO_EXEMPLO = "id-do-modelo"
TIMEOUT_PADRAO_S = 30


@dataclass(frozen=True)
class Configuracao:
    api_key: str
    modelo: str
    timeout_s: int

    def __repr__(self) -> str:
        # Evita que a chave apareça sem querer em prints ou logs.
        return f"Configuracao(api_key='***', modelo={self.modelo!r}, timeout_s={self.timeout_s})"


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

    timeout_txt = (os.getenv("GEMINI_TIMEOUT") or str(TIMEOUT_PADRAO_S)).strip()
    try:
        timeout_s = int(timeout_txt)
    except ValueError:
        timeout_s = 0
    if timeout_s <= 0:
        raise ErroConfiguracao("GEMINI_TIMEOUT deve ser um número inteiro positivo, em segundos.")

    return Configuracao(api_key=api_key, modelo=modelo, timeout_s=timeout_s)