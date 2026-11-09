"""P0 - Ficha de artigo: transforma o abstract de um artigo em uma ficha estruturada."""

import os
import sys

from dotenv import load_dotenv
from google import genai

MODELO = "gemini-3.5-flash-lite"

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


def gerar_ficha(abstract: str) -> str:
    """Envia o abstract ao Gemini e devolve a ficha em texto."""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resposta = client.models.generate_content(
        model=MODELO,
        contents=PROMPT.format(abstract=abstract),
    )
    return resposta.text


def main() -> None:
    load_dotenv()
    print("Cole o abstract e finalize com uma linha vazia + Ctrl+D (Linux/Mac) ou Ctrl+Z e Enter (Windows):\n")
    abstract = sys.stdin.read().strip()
    ficha = gerar_ficha(abstract)
    print("\n--- FICHA ---\n")
    print(ficha)


if __name__ == "__main__":
    main()