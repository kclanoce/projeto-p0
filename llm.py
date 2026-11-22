"""Comunicação com o Gemini: cria o cliente, faz a chamada e traduz falhas em erros claros."""

import httpx
from google import genai
from google.genai import errors, types

from config import Configuracao
from erros import ErroApp, ErroComunicacao, ErroConfiguracao, ErroCredencial, ErroServico


def criar_cliente(config: Configuracao) -> genai.Client:
    # O timeout do SDK é em milissegundos.
    return genai.Client(
        api_key=config.api_key,
        http_options=types.HttpOptions(timeout=config.timeout_s * 1000),
    )


def _traduzir_erro_api(erro: errors.APIError) -> ErroApp:
    codigo = getattr(erro, "code", None)
    mensagem = str(getattr(erro, "message", "") or erro).lower()
    chave_recusada = "api key" in mensagem or "api_key" in mensagem

    if codigo in (401, 403) or (codigo == 400 and chave_recusada):
        return ErroCredencial(
            "O serviço recusou a chave de API. Verifique se GEMINI_API_KEY no arquivo .env "
            "está correta e ativa."
        )
    if codigo == 404:
        return ErroConfiguracao(
            "O modelo configurado não foi encontrado ou não está disponível. "
            "Confira GEMINI_MODEL no arquivo .env."
        )
    if codigo == 429:
        return ErroServico("O limite de uso do serviço foi atingido. Aguarde um pouco e tente novamente.")
    if isinstance(codigo, int) and codigo >= 500:
        return ErroServico(
            "O serviço está indisponível ou sobrecarregado no momento. Tente novamente em alguns minutos."
        )
    return ErroServico(f"O serviço recusou a solicitação (código {codigo}).")


def chamar_modelo(cliente, modelo: str, prompt: str):
    """Envia o prompt ao modelo. Qualquer falha vira um erro com mensagem compreensível."""
    try:
        return cliente.models.generate_content(model=modelo, contents=prompt)
    except errors.APIError as erro:
        raise _traduzir_erro_api(erro) from erro
    except httpx.TimeoutException as erro:
        raise ErroComunicacao(
            "O serviço demorou demais para responder (timeout). Tente novamente "
            "ou aumente GEMINI_TIMEOUT no arquivo .env."
        ) from erro
    except (httpx.HTTPError, ConnectionError, TimeoutError) as erro:
        raise ErroComunicacao(
            "Não foi possível falar com o serviço. Verifique sua conexão com a internet."
        ) from erro