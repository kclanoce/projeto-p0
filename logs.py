"""Registros simples da execução. Só gravam tamanhos, tempos e tipos de erro:
nunca chaves, abstracts nem respostas do modelo."""

import logging

NOME_BASE = "p0"
FORMATO = "%(asctime)s %(levelname)s %(name)s: %(message)s"

# Evita que registros apareçam no terminal quando os logs ainda não foram configurados.
logging.getLogger(NOME_BASE).addHandler(logging.NullHandler())


def obter_logger(nome: str) -> logging.Logger:
    return logging.getLogger(f"{NOME_BASE}.{nome}")


def configurar_logs(nivel: str, arquivo: str) -> None:
    """Grava os registros em um arquivo (e não no terminal, para não misturar com a ficha)."""
    base = logging.getLogger(NOME_BASE)
    for handler in list(base.handlers):
        if isinstance(handler, logging.FileHandler):
            base.removeHandler(handler)
            handler.close()

    base.setLevel(getattr(logging, nivel.upper(), logging.INFO))
    base.propagate = False

    try:
        handler = logging.FileHandler(arquivo, encoding="utf-8")
    except OSError:
        return  # sem permissão para gravar o arquivo: o programa segue sem registros
    handler.setFormatter(logging.Formatter(FORMATO))
    base.addHandler(handler)