"""Configuração de objetos compartilhados para a aplicação web2py.

Este módulo inicializa o gerenciador de entidades e fornece um utilitário para
recuperar o jogador associado à sessão atual.
"""

from gluon import current

from package.gerenciador_entidades import GerenciadorEntidades
from package.jogador import Jogador

# O gerenciador é criado uma única vez e armazenado no objeto ``current`` para
# ser reutilizado pelos controladores e visões.
if not hasattr(current, "gerenciador_entidades"):
    current.gerenciador_entidades = GerenciadorEntidades()


def obter_jogador(nome_padrao: str = "Convidado") -> Jogador:
    """Retorna uma instância de :class:`Jogador` vinculada à sessão atual.

    O nome do jogador é mantido na sessão web2py, permitindo personalização
    futura caso uma tela de login seja adicionada. Caso nenhum nome esteja
    definido, utiliza-se ``nome_padrao``.
    """

    session = current.session
    if not session.get("jogador_nome"):
        session.jogador_nome = nome_padrao
    return Jogador(session.jogador_nome)
