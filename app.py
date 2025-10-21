"""Aplicação web com Bottle para o Laboratório de Quimeras."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from bottle import Bottle, TEMPLATE_PATH, request, response, template

from package.gerenciador_entidades import Entidade, GerenciadorEntidades
from package.jogador import Jogador

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH.insert(0, str(BASE_DIR / "templates"))

app = Bottle()
gerenciador = GerenciadorEntidades()
COOKIE_SECRET = "chimera-secret"  # Em produção utilize um valor seguro obtido de variáveis de ambiente.


def _ordenar_nomes(nomes: Iterable[str]) -> List[str]:
    return sorted(set(nomes))


def obter_jogador(nome_padrao: str = "Convidado") -> Jogador:
    """Retorna uma instância de :class:`Jogador` associada ao visitante atual."""

    nome = request.get_cookie("jogador_nome", secret=COOKIE_SECRET)
    if not nome:
        nome = nome_padrao
        response.set_cookie("jogador_nome", nome, secret=COOKIE_SECRET, path="/")
    return Jogador(nome)


@app.get("/")
@app.post("/")
def index():  # pragma: no cover - função exercitada via navegação manual
    """Exibe a página principal com o formulário de fusão de criaturas."""

    jogador = obter_jogador()
    selecionadas = request.forms.getall("criaturas") if request.method == "POST" else []

    mensagem = None
    novas_criaturas: List[Entidade] = []

    if request.method == "POST":
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
                    mensagem = "Fusão concluída! Novas criaturas foram adicionadas ao seu códex."
                else:
                    mensagem = "Nenhuma combinação conhecida para as criaturas escolhidas."

    descobertas = _ordenar_nomes(jogador.criaturas_descobertas)

    return template(
        "index",
        mensagem=mensagem,
        descobertas=descobertas,
        selecionadas=selecionadas,
        novas_criaturas=novas_criaturas,
        jogador=jogador,
    )


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=8000, debug=True, reloader=True)
