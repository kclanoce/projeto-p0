"""P0 - Ficha de artigo: ponto de entrada. Orquestra as etapas e conversa com o usuário."""

import sys

from config import Configuracao, carregar_configuracao
from erros import ErroApp
from ficha import montar_prompt, tratar_resposta, validar_entrada
from llm import chamar_modelo, criar_cliente


def ler_entrada() -> str:
    print("Cole o abstract do artigo.")
    print("Para finalizar: nova linha, depois Ctrl+Z e Enter (Windows) ou Ctrl+D (Linux/Mac).\n")
    return sys.stdin.read()


def gerar_ficha(abstract: str, config: Configuracao, cliente=None) -> str:
    """Prepara o prompt, chama o modelo e trata a resposta."""
    prompt = montar_prompt(abstract)
    cliente = cliente or criar_cliente(config)
    resposta = chamar_modelo(cliente, config.modelo, prompt)
    return tratar_resposta(getattr(resposta, "text", None))


def exibir_ficha(ficha: str) -> None:
    print("\n--- FICHA ---\n")
    print(ficha)


def main() -> int:
    try:
        config = carregar_configuracao()
        abstract = validar_entrada(ler_entrada())
        ficha = gerar_ficha(abstract, config)
    except ErroApp as erro:
        print(f"\nErro: {erro}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nExecução cancelada.", file=sys.stderr)
        return 130
    except Exception as erro:  # rede de segurança para falhas não previstas
        print(f"\nErro inesperado ({type(erro).__name__}). Tente novamente.", file=sys.stderr)
        return 1

    exibir_ficha(ficha)
    return 0


if __name__ == "__main__":
    sys.exit(main())