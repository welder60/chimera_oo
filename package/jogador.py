import os
import pickle


class Jogador:
    def __init__(self, nome, arquivo_progresso="dados_jogador.pkl"):
        self._nome = nome
        self._arquivo_progresso = arquivo_progresso
        self._criaturas_descobertas = set()
        self._creditos = 0
        self._carregar_progresso()

    def _carregar_progresso(self):
        if not os.path.exists(self._arquivo_progresso):
            return
        try:
            with open(self._arquivo_progresso, "rb") as arquivo:
                dados = pickle.load(arquivo)
                progresso = dados.get(self._nome)
                if isinstance(progresso, dict):
                    criaturas = progresso.get("criaturas", [])
                    creditos = progresso.get("creditos", 0)
                elif progresso is None:
                    criaturas = []
                    creditos = 0
                else:
                    criaturas = progresso
                    creditos = 0
                self._criaturas_descobertas = set(criaturas)
                self._creditos = int(creditos)
        except (pickle.PickleError, EOFError, AttributeError, ValueError):
            self._criaturas_descobertas = set()
            self._creditos = 0

    def _salvar_progresso(self):
        dados = {}
        if os.path.exists(self._arquivo_progresso):
            try:
                with open(self._arquivo_progresso, "rb") as arquivo:
                    dados = pickle.load(arquivo)
            except (pickle.PickleError, EOFError, AttributeError, ValueError):
                dados = {}
        dados[self._nome] = {
            "criaturas": list(self._criaturas_descobertas),
            "creditos": self._creditos,
        }
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

    @property
    def creditos(self):
        return self._creditos

    def adicionar_creditos(self, quantidade: int):
        if quantidade < 0:
            raise ValueError("A quantidade de créditos deve ser não negativa.")
        if quantidade == 0:
            return
        self._creditos += quantidade
        self._salvar_progresso()

    def tem_creditos(self, quantidade: int) -> bool:
        if quantidade < 0:
            raise ValueError("A quantidade de créditos deve ser não negativa.")
        return self._creditos >= quantidade

    def gastar_creditos(self, quantidade: int) -> bool:
        if quantidade < 0:
            raise ValueError("A quantidade de créditos deve ser não negativa.")
        if self._creditos < quantidade:
            return False
        if quantidade == 0:
            return True
        self._creditos -= quantidade
        self._salvar_progresso()
        return True
