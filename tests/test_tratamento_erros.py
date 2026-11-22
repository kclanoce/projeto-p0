"""Testes do P0 com integração simulada (mock): não chamam o Gemini e não gastam cota."""

import io
import os
import unittest
from contextlib import redirect_stderr
from unittest.mock import Mock, patch

import httpx
from google.genai.errors import ClientError, ServerError

import app
from config import Configuracao, carregar_configuracao
from erros import (
    ErroComunicacao,
    ErroConfiguracao,
    ErroCredencial,
    ErroEntrada,
    ErroResposta,
    ErroServico,
)
from ficha import tratar_resposta, validar_entrada
from llm import chamar_modelo

CHAVE_FALSA = "chave-falsa-para-teste-123"
CONFIG_TESTE = Configuracao(api_key=CHAVE_FALSA, modelo="modelo-de-teste", timeout_s=5)
FICHA_VALIDA = (
    "- Método: autoencoder baseado em transformer\n"
    "- Dataset(s): SMD e SMAP\n"
    "- Métrica(s): F1-score\n"
    "- Principal resultado: F1 de 0.91"
)


def erro_api(classe, codigo, mensagem, status):
    corpo = {"error": {"code": codigo, "message": mensagem, "status": status}}
    return classe(codigo, corpo, None)


def cliente_que_falha(excecao):
    cliente = Mock()
    cliente.models.generate_content.side_effect = excecao
    return cliente


def cliente_que_responde(texto):
    cliente = Mock()
    cliente.models.generate_content.return_value = Mock(text=texto)
    return cliente


class TestConfiguracao(unittest.TestCase):
    def carregar(self, **variaveis):
        with patch.dict(os.environ, variaveis, clear=True):
            return carregar_configuracao(ler_dotenv=False)

    def test_credencial_ausente(self):
        with self.assertRaises(ErroCredencial):
            self.carregar(GEMINI_MODEL="modelo")

    def test_credencial_com_valor_de_exemplo(self):
        with self.assertRaises(ErroCredencial):
            self.carregar(GEMINI_API_KEY="coloque_sua_chave_aqui", GEMINI_MODEL="modelo")

    def test_modelo_ausente(self):
        with self.assertRaises(ErroConfiguracao):
            self.carregar(GEMINI_API_KEY=CHAVE_FALSA)

    def test_timeout_invalido(self):
        for valor in ("abc", "0", "-3"):
            with self.subTest(valor=valor):
                with self.assertRaises(ErroConfiguracao):
                    self.carregar(GEMINI_API_KEY=CHAVE_FALSA, GEMINI_MODEL="m", GEMINI_TIMEOUT=valor)

    def test_configuracao_valida_usa_timeout_padrao(self):
        config = self.carregar(GEMINI_API_KEY=CHAVE_FALSA, GEMINI_MODEL="m")
        self.assertEqual(config.timeout_s, 30)

    def test_repr_nao_expoe_a_chave(self):
        config = self.carregar(GEMINI_API_KEY=CHAVE_FALSA, GEMINI_MODEL="m")
        self.assertNotIn(CHAVE_FALSA, repr(config))


class TestEntrada(unittest.TestCase):
    def test_entrada_vazia_ou_so_espacos(self):
        for texto in ("", "   \n  ", None):
            with self.subTest(texto=texto):
                with self.assertRaises(ErroEntrada):
                    validar_entrada(texto)

    def test_entrada_muito_longa(self):
        with self.assertRaises(ErroEntrada):
            validar_entrada("a" * 9000)

    def test_entrada_valida_e_limpa(self):
        self.assertEqual(validar_entrada("  texto  \n"), "texto")


class TestChamadaAoModelo(unittest.TestCase):
    def test_credencial_invalida_nao_expoe_segredo(self):
        casos = [
            erro_api(ClientError, 400, "API key not valid. Please pass a valid API key.", "INVALID_ARGUMENT"),
            erro_api(ClientError, 403, "Permission denied.", "PERMISSION_DENIED"),
        ]
        for erro in casos:
            with self.subTest(codigo=erro.code):
                with self.assertRaises(ErroCredencial) as ctx:
                    chamar_modelo(cliente_que_falha(erro), "modelo", "prompt")
                self.assertNotIn(CHAVE_FALSA, str(ctx.exception))

    def test_modelo_nao_encontrado(self):
        erro = erro_api(ClientError, 404, "model not found", "NOT_FOUND")
        with self.assertRaises(ErroConfiguracao):
            chamar_modelo(cliente_que_falha(erro), "modelo", "prompt")

    def test_limite_de_uso(self):
        erro = erro_api(ClientError, 429, "quota exceeded", "RESOURCE_EXHAUSTED")
        with self.assertRaises(ErroServico):
            chamar_modelo(cliente_que_falha(erro), "modelo", "prompt")

    def test_servico_indisponivel(self):
        erro = erro_api(ServerError, 503, "high demand", "UNAVAILABLE")
        with self.assertRaises(ErroServico):
            chamar_modelo(cliente_que_falha(erro), "modelo", "prompt")

    def test_timeout(self):
        with self.assertRaises(ErroComunicacao) as ctx:
            chamar_modelo(cliente_que_falha(httpx.ReadTimeout("lento")), "modelo", "prompt")
        self.assertIn("timeout", str(ctx.exception).lower())

    def test_falha_de_comunicacao(self):
        with self.assertRaises(ErroComunicacao):
            chamar_modelo(cliente_que_falha(httpx.ConnectError("sem rede")), "modelo", "prompt")


class TestResposta(unittest.TestCase):
    def test_resposta_vazia(self):
        for texto in (None, "", "   "):
            with self.subTest(texto=texto):
                with self.assertRaises(ErroResposta):
                    tratar_resposta(texto)

    def test_formato_inesperado(self):
        with self.assertRaises(ErroResposta):
            tratar_resposta("Desculpe, não consegui ajudar com isso.")

    def test_resposta_valida(self):
        self.assertEqual(tratar_resposta(FICHA_VALIDA), FICHA_VALIDA)


class TestFluxoCompleto(unittest.TestCase):
    def test_gerar_ficha_com_sucesso(self):
        ficha = app.gerar_ficha("abstract qualquer", CONFIG_TESTE, cliente_que_responde(FICHA_VALIDA))
        self.assertIn("SMD e SMAP", ficha)

    def test_gerar_ficha_com_resposta_vazia(self):
        with self.assertRaises(ErroResposta):
            app.gerar_ficha("abstract qualquer", CONFIG_TESTE, cliente_que_responde(None))

    def test_main_encerra_com_mensagem_quando_credencial_ausente(self):
        erro = ErroCredencial("A chave de API não foi configurada.")
        saida_erro = io.StringIO()
        with patch("app.carregar_configuracao", side_effect=erro), redirect_stderr(saida_erro):
            codigo = app.main()
        self.assertEqual(codigo, 1)
        self.assertIn("A chave de API não foi configurada.", saida_erro.getvalue())
        self.assertNotIn("Traceback", saida_erro.getvalue())


if __name__ == "__main__":
    unittest.main()