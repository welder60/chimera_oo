"""Controladores web2py responsáveis pela interface de fusão de criaturas."""

from gluon import current
from gluon.html import BUTTON, DIV, H3, LI, OPTION, P, SELECT, UL

from ..models.db import obter_jogador
from package.gerenciador_entidades import Entidade


def index():
    """Página principal que lista criaturas descobertas e permite fusões."""

    request = current.request
    response = current.response

    gerenciador = current.gerenciador_entidades
    jogador = obter_jogador()

    descobertas = sorted(jogador.criaturas_descobertas)
    selecionadas = request.post_vars.getlist("criaturas") if request.env.request_method == "POST" else []

    mensagem = None
    novas_criaturas: list[Entidade] = []

    if request.env.request_method == "POST":
        if len(selecionadas) < 2:
            mensagem = "Selecione pelo menos duas criaturas para realizar a fusão."
        else:
            entidades_escolhidas = gerenciador.get(selecionadas)
            if len(entidades_escolhidas) != len(selecionadas):
                mensagem = "Algumas criaturas selecionadas não foram encontradas no gerenciador."
            else:
                novas_criaturas = gerenciador.cruzar(entidades_escolhidas)
                if novas_criaturas:
                    for entidade in novas_criaturas:
                        jogador.registrar_fusao(entidade._nome)
                    descobertas = sorted(jogador.criaturas_descobertas)
                    mensagem = "Fusão concluída! Novas criaturas foram adicionadas ao seu códex."
                else:
                    mensagem = "Nenhuma combinação conhecida para as criaturas escolhidas."

    response.title = "Laboratório de Quimeras"

    opcoes = [OPTION(nome, _value=nome, _selected=nome in selecionadas) for nome in descobertas]
    formulario = DIV(
        H3("Fundir criaturas"),
        P("Selecione duas ou mais criaturas descobertas e tente criar novas combinações."),
        DIV(
            SELECT(
                *opcoes,
                _name="criaturas",
                _multiple="multiple",
                _size="8",
                _class="form-control",
            ),
            _class="mb-3",
        ),
        BUTTON("Fundir", _type="submit", _class="btn btn-primary"),
        _class="fusion-form",
    )

    lista_descobertas = UL(
        *[LI(nome) for nome in descobertas] if descobertas else [LI("Nenhuma criatura descoberta ainda.")]
    )

    lista_resultados = (
        UL(
            *[
                LI(f"{entidade._nome} (tags: {', '.join(sorted(entidade._tags))})")
                for entidade in novas_criaturas
            ]
        )
        if novas_criaturas
        else None
    )

    return dict(
        formulario=formulario,
        lista_descobertas=lista_descobertas,
        lista_resultados=lista_resultados,
        mensagem=mensagem,
        selecionadas=selecionadas,
    )
