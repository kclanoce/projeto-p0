"""Regras do problema: validar a entrada, montar o prompt e checar a ficha devolvida."""

import unicodedata

from erros import ErroEntrada, ErroResposta

LIMITE_CARACTERES = 8000
CAMPOS_ESPERADOS = ("metodo", "dataset", "metrica", "principal resultado")

PROMPT = """Você recebe o abstract de um artigo científico sobre detecção de anomalias.
Devolva uma ficha com exatamente estes campos, em português:

- Método:
- Dataset(s):
- Métrica(s):
- Principal resultado:

Se alguma informação não estiver no texto, escreva "não informado".
Não invente nada além do que está no abstract.

Abstract:
{abstract}
"""


def validar_entrada(texto: str | None) -> str:
    """Impede entradas vazias ou grandes demais."""
    texto = (texto or "").strip()
    if not texto:
        raise ErroEntrada("Nenhum texto foi informado. Cole o abstract do artigo e tente de novo.")
    if len(texto) > LIMITE_CARACTERES:
        raise ErroEntrada(
            f"O texto tem {len(texto)} caracteres e o limite é {LIMITE_CARACTERES}. "
            "Envie apenas o abstract do artigo."
        )
    return texto


def montar_prompt(abstract: str) -> str:
    return PROMPT.format(abstract=abstract)


def _sem_acentos(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn").lower()


def tratar_resposta(texto: str | None) -> str:
    """Confere se a resposta não veio vazia e se tem os quatro campos da ficha."""
    if texto is None or not texto.strip():
        raise ErroResposta("O modelo devolveu uma resposta vazia. Tente novamente.")
    normalizado = _sem_acentos(texto)
    if any(campo not in normalizado for campo in CAMPOS_ESPERADOS):
        raise ErroResposta(
            "A resposta do modelo veio em formato inesperado (faltam campos da ficha). "
            "Tente novamente."
        )
    return texto.strip()