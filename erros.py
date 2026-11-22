"""Erros previstos pela aplicação. Cada um carrega uma mensagem pensada para o usuário."""


class ErroApp(Exception):
    """Base de todos os erros previstos."""


class ErroEntrada(ErroApp):
    """Entrada vazia ou inadequada."""


class ErroConfiguracao(ErroApp):
    """Configuração ausente ou inválida (modelo, timeout...)."""


class ErroCredencial(ErroApp):
    """Chave de API ausente ou recusada pelo serviço."""


class ErroServico(ErroApp):
    """Serviço indisponível, com limite excedido ou que recusou a solicitação."""


class ErroComunicacao(ErroApp):
    """Falha de rede ou timeout."""


class ErroResposta(ErroApp):
    """Resposta vazia ou em formato inesperado."""