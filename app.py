"""P0 - Ficha de artigo: ponto de entrada. Orquestra as etapas e conversa com o usuário."""

import sys

from config import Configuracao, carregar_configuracao
from erros import ErroApp
from ficha import montar_prompt, tratar_resposta, validar_entrada
from llm import chamar_modelo, criar_cliente, criar_config_geracao
from logs import configurar_logs, obter_logger

logger = obter_logger("app")


def ler_entrada() -> str:
    print("Cole o abstract do artigo.")
    print("Para finalizar: nova linha, depois Ctrl+Z e Enter (Windows) ou Ctrl+D (Linux/Mac).\n")
    return sys.stdin.read()


def gerar_ficha(abstract: str, config: Configuracao, cliente=None) -> str:
    """Prepara o prompt, chama o modelo e trata a resposta."""
    prompt = montar_prompt(abstract)
    cliente = cliente or criar_cliente(config)
    resposta = chamar_modelo(cliente, config.modelo, prompt, criar_config_geracao(config))
    ficha = tratar_resposta(getattr(resposta, "text", None))
    logger.info("Ficha gerada (%d caracteres)", len(ficha))
    return ficha


def exibir_ficha(ficha: str) -> None:
    print("\n--- FICHA ---\n")
    print(ficha)


def main() -> int:
    try:
        config = carregar_configuracao()
        configurar_logs(config.nivel_log, config.arquivo_log)
        logger.info(
            "Execução iniciada (modelo=%s, max_tokens=%d, temperatura=%s)",
            config.modelo,
            config.max_output_tokens,
            config.temperatura,
        )
        abstract = validar_entrada(ler_entrada())
        logger.info("Entrada validada (%d caracteres)", len(abstract))
        ficha = gerar_ficha(abstract, config)
    except ErroApp as erro:
        logger.error("Execução encerrada com %s", type(erro).__name__)
        print(f"\nErro: {erro}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nExecução cancelada.", file=sys.stderr)
        return 130
    except Exception as erro:  # rede de segurança para falhas não previstas
        logger.error("Erro inesperado: %s", type(erro).__name__)
        print(f"\nErro inesperado ({type(erro).__name__}). Tente novamente.", file=sys.stderr)
        return 1

    exibir_ficha(ficha)
    logger.info("Execução concluída")
    return 0


if __name__ == "__main__":
    sys.exit(main())