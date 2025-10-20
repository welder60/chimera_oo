import os
import pickle


class Jogador:
    def __init__(self, nome, arquivo_progresso="dados_jogador.pkl"):
        self._nome = nome
        self._arquivo_progresso = arquivo_progresso
        self._criaturas_descobertas = set()
        self._carregar_progresso()

    def _carregar_progresso(self):
        if not os.path.exists(self._arquivo_progresso):
            return
        try:
            with open(self._arquivo_progresso, "rb") as arquivo:
                dados = pickle.load(arquivo)
                self._criaturas_descobertas = set(dados.get(self._nome, []))
        except (pickle.PickleError, EOFError, AttributeError, ValueError):
            self._criaturas_descobertas = set()

    def _salvar_progresso(self):
        dados = {}
        if os.path.exists(self._arquivo_progresso):
            try:
                with open(self._arquivo_progresso, "rb") as arquivo:
                    dados = pickle.load(arquivo)
            except (pickle.PickleError, EOFError, AttributeError, ValueError):
                dados = {}
        dados[self._nome] = list(self._criaturas_descobertas)
        with open(self._arquivo_progresso, "wb") as arquivo:
            pickle.dump(dados, arquivo)

    def registrar_fusao(self, criatura):
        if criatura not in self._criaturas_descobertas:
            self._criaturas_descobertas.add(criatura)
            self._salvar_progresso()

    @property
    def criaturas_descobertas(self):
        return set(self._criaturas_descobertas)

    @property
    def quantidade_descobertas(self):
        return len(self._criaturas_descobertas)
