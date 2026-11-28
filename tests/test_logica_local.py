"""Testes da lógica local do P0. Nenhum deles faz chamada real ao LLM."""

import io
import os
import unittest
from contextlib import redirect_stderr
from unittest.mock import Mock, patch

import httpx

import app
from config import Configuracao, carregar_configuracao
from erros import ErroConfiguracao
from ficha import montar_prompt
from llm import chamar_modelo, criar_config_geracao

CHAVE_FALSA = "chave-falsa-para-teste-123"
ABSTRACT_SECRETO = "TEXTO-CONFIDENCIAL-DO-ARTIGO-XYZ"
FICHA = (
    "- Método: autoencoder baseado em transformer\n"
    "- Dataset(s): SMD e SMAP\n"
    "- Métrica(s): F1-score\n"
    "- Principal resultado: F1 de 0.91"
)


def carregar(**extra):
    variaveis = {"GEMINI_API_KEY": CHAVE_FALSA, "GEMINI_MODEL": "m"}
    variaveis.update(extra)
    with patch.dict(os.environ, variaveis, clear=True):
        return carregar_configuracao(ler_dotenv=False)


def cliente_que_responde(texto):
    cliente = Mock()
    cliente.models.generate_content.return_value = Mock(text=texto)
    return cliente


class TestPreparacaoDaSolicitacao(unittest.TestCase):
    def test_prompt_contem_o_abstract_e_os_campos_da_ficha(self):
        prompt = montar_prompt("abstract de teste")
        self.assertIn("abstract de teste", prompt)
        for campo in ("Método", "Dataset", "Métrica", "Principal resultado"):
            self.assertIn(campo, prompt)


class TestParametrosDeGeracao(unittest.TestCase):
    def test_valores_padrao(self):
        config = carregar()
        self.assertEqual(config.max_output_tokens, 2048)
        self.assertEqual(config.temperatura, 0.2)

    def test_valores_vindos_do_ambiente(self):
        config = carregar(GEMINI_MAX_OUTPUT_TOKENS="512", GEMINI_TEMPERATURE="0,7")
        self.assertEqual(config.max_output_tokens, 512)
        self.assertEqual(config.temperatura, 0.7)

    def test_valores_invalidos(self):
        casos = {
            "GEMINI_MAX_OUTPUT_TOKENS": ["abc", "0", "-1"],
            "GEMINI_TEMPERATURE": ["abc", "3", "-0.1"],
            "LOG_LEVEL": ["FALADOR"],
        }
        for nome, valores in casos.items():
            for valor in valores:
                with self.subTest(variavel=nome, valor=valor):
                    with self.assertRaises(ErroConfiguracao):
                        carregar(**{nome: valor})

    def test_parametros_chegam_ao_modelo_sem_alterar_o_codigo(self):
        config = carregar(GEMINI_MAX_OUTPUT_TOKENS="256", GEMINI_TEMPERATURE="0.5")
        geracao = criar_config_geracao(config)
        self.assertEqual(geracao.max_output_tokens, 256)
        self.assertEqual(geracao.temperature, 0.5)

        cliente = cliente_que_responde(FICHA)
        app.gerar_ficha("abstract", config, cliente)
        enviados = cliente.models.generate_content.call_args.kwargs
        self.assertEqual(enviados["model"], "m")
        self.assertEqual(enviados["config"].max_output_tokens, 256)


class TestRegistros(unittest.TestCase):
    def test_logs_nao_contem_segredos_nem_conteudo(self):
        config = Configuracao(api_key=CHAVE_FALSA, modelo="m", timeout_s=5)
        with self.assertLogs("p0", level="INFO") as capturado:
            app.gerar_ficha(ABSTRACT_SECRETO, config, cliente_que_responde(FICHA))
        texto = "\n".join(capturado.output)
        self.assertTrue(capturado.records)
        self.assertNotIn(CHAVE_FALSA, texto)
        self.assertNotIn(ABSTRACT_SECRETO, texto)
        self.assertNotIn("autoencoder", texto)

    def test_logs_de_falha_nao_vazam_a_mensagem_do_erro(self):
        cliente = Mock()
        cliente.models.generate_content.side_effect = httpx.ConnectError(f"falha com {CHAVE_FALSA}")
        with self.assertLogs("p0", level="INFO") as capturado:
            with self.assertRaises(Exception):
                chamar_modelo(cliente, "m", "prompt")
        self.assertNotIn(CHAVE_FALSA, "\n".join(capturado.output))


class TestFluxoPrincipal(unittest.TestCase):
    def test_main_rejeita_entrada_vazia_sem_chamar_o_llm(self):
        config = Configuracao(api_key=CHAVE_FALSA, modelo="m", timeout_s=5)
        saida = io.StringIO()
        with patch("app.carregar_configuracao", return_value=config), \
             patch("app.configurar_logs"), \
             patch("app.ler_entrada", return_value="   "), \
             patch("app.criar_cliente") as criar, \
             redirect_stderr(saida):
            codigo = app.main()
        self.assertEqual(codigo, 1)
        criar.assert_not_called()
        self.assertIn("Nenhum texto", saida.getvalue())


if __name__ == "__main__":
    unittest.main()