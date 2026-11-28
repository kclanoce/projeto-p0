"""Comunicação com o Gemini: cria o cliente, faz a chamada e traduz falhas em erros claros."""

import time

import httpx
from google import genai
from google.genai import errors, types

from config import Configuracao
from erros import ErroApp, ErroComunicacao, ErroConfiguracao, ErroCredencial, ErroServico
from logs import obter_logger

logger = obter_logger("llm")


def criar_cliente(config: Configuracao) -> genai.Client:
    # O timeout do SDK é em milissegundos.
    return genai.Client(
        api_key=config.api_key,
        http_options=types.HttpOptions(timeout=config.timeout_s * 1000),
    )


def criar_config_geracao(config: Configuracao) -> types.GenerateContentConfig:
    """Parâmetros de geração vindos da configuração, sem mexer no núcleo da aplicação."""
    return types.GenerateContentConfig(
        max_output_tokens=config.max_output_tokens,
        temperature=config.temperatura,
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


def chamar_modelo(cliente, modelo: str, prompt: str, config_geracao=None):
    """Envia o prompt ao modelo. Qualquer falha vira um erro com mensagem compreensível."""
    parametros = {"model": modelo, "contents": prompt}
    if config_geracao is not None:
        parametros["config"] = config_geracao

    inicio = time.monotonic()
    logger.info("Chamando o modelo %s (prompt com %d caracteres)", modelo, len(prompt))
    try:
        resposta = cliente.models.generate_content(**parametros)
    except errors.APIError as erro:
        logger.warning(
            "Falha da API (código %s) após %.1fs", getattr(erro, "code", None), time.monotonic() - inicio
        )
        raise _traduzir_erro_api(erro) from erro
    except httpx.TimeoutException as erro:
        logger.warning("Timeout após %.1fs", time.monotonic() - inicio)
        raise ErroComunicacao(
            "O serviço demorou demais para responder (timeout). Tente novamente "
            "ou aumente GEMINI_TIMEOUT no arquivo .env."
        ) from erro
    except (httpx.HTTPError, ConnectionError, TimeoutError) as erro:
        logger.warning(
            "Falha de comunicação (%s) após %.1fs", type(erro).__name__, time.monotonic() - inicio
        )
        raise ErroComunicacao(
            "Não foi possível falar com o serviço. Verifique sua conexão com a internet."
        ) from erro

    logger.info("Resposta recebida em %.1fs", time.monotonic() - inicio)
    return resposta