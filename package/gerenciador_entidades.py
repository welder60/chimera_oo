import csv
from package.entidade import Entidade


PREDEFINED_ENTIDADES = [
  {"nome": "ave", "tags": ["AVE"], "imagem": "assets/ave.png"},
  {"nome": "cavalo", "tags": ["CAVALO"], "imagem": "assets/cavalo.png"},
  {"nome": "centauro", "tags": ["HUMANO", "CAVALO"], "imagem": "assets/centauro.png"},
  {"nome": "esfinge", "tags": ["HUMANO", "LEAO", "AVE"], "imagem": "assets/esfinge.png"},
  {"nome": "grifo", "tags": ["AVE", "LEAO"], "imagem": "assets/grifo.png"},
  {"nome": "hipocampo", "tags": ["CAVALO", "PEIXE"], "imagem": "assets/hipocampo.png"},
  {"nome": "hipogrifo", "tags": ["CAVALO", "AVE", "LEAO"], "imagem": "assets/hipogrifo.png"},
  {"nome": "humano", "tags": ["HUMANO"], "imagem": "assets/humano.png"},
  {"nome": "leao", "tags": ["LEAO"], "imagem": "assets/leao.png"},
  {"nome": "minotauro", "tags": ["CHIFRES", "HUMANO"], "imagem": "assets/minotauro.png"},
  {"nome": "minotauro alado", "tags": ["CHIFRES", "HUMANO", "AVE"], "imagem": "assets/minotauro_alado.png"},
  {"nome": "pegasus", "tags": ["CAVALO", "AVE"], "imagem": "assets/pegasus.png"},
  {"nome": "peixe", "tags": ["PEIXE"], "imagem": "assets/peixe.png"},
  {"nome": "sereia", "tags": ["HUMANO", "PEIXE"], "imagem": "assets/sereia.png"},
  {"nome": "touro", "tags": ["CHIFRES"], "imagem": "assets/touro.png"},
  {"nome": "unicornio", "tags": ["CAVALO", "CHIFRES"], "imagem": "assets/unicornio.png"},
  {"nome": "unicornio alado", "tags": ["CAVALO", "CHIFRES", "AVE"], "imagem": "assets/unicornio_alado.png"},
  {"nome": "anjo", "tags": ["HUMANO", "AVE"], "imagem": "assets/anjo.png"}
]



class GerenciadorEntidades:

    def __init__(self):
        self._entidades = []
        self._carregar_predefinidas()

    def _carregar_predefinidas(self):
        for dados in PREDEFINED_ENTIDADES:
            entidade = Entidade(
                dados["nome"], dados["tags"], dados.get("imagem")
            )
            self._entidades.append(entidade)

    def adicionar(self, entidade: Entidade):
        self._entidades.append(entidade)

    def carregar_csv(self, caminho_csv: str, delimitador: str = ","):
        with open(caminho_csv, newline="", encoding="utf-8") as csvfile:
            leitor = csv.DictReader(csvfile, delimiter=delimitador)
            for linha in leitor:
                nome = linha["nome"].strip()
                tags = [t.strip() for t in linha["tags"].split(";")]
                caminho_imagem = linha.get("imagem")
                if caminho_imagem is not None:
                    caminho_imagem = caminho_imagem.strip() or None
                entidade = Entidade(nome, tags, caminho_imagem)
                self.adicionar(entidade)

    def get(self, nomes):
        resultado = []
        for nome in nomes:
            for _entidade in self._entidades:
                if _entidade._nome == nome:
                    resultado.append(_entidade)
        return resultado

    def listar_nomes(self):
        return sorted(entidade._nome for entidade in self._entidades)

    def listar_basicas(self):
        return sorted(
            (entidade for entidade in self._entidades if len(entidade._tags) == 1),
            key=lambda entidade: entidade._nome,
        )

    def cruzar(self, entidades):
        resultado = []
        for _entidade in self._entidades:
            tags_entidade = set(_entidade._tags)
            compativel = True
            for entidade in entidades:
                alteracao = tags_entidade - entidade._tags
                if len(alteracao) >= len(tags_entidade):
                    compativel = False
                    break
                tags_entidade = tags_entidade - entidade._tags
            if len(tags_entidade) > 0:
                compativel = False
            if compativel:
                resultado.append(_entidade)
        return resultado

    def evolucoes(self, entidade):
        resultado = []
        for _entidade in self._entidades:
            if _entidade != entidade and _entidade.contem(entidade):
                resultado.append(_entidade)
        return resultado

    def derivacoes(self, entidade):
        resultado = []
        for _entidade in self._entidades:
            if _entidade != entidade and entidade.contem(_entidade):
                resultado.append(_entidade)
        return resultado
