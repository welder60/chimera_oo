class Entidade:

    def __init__(self, nome, tags, caminho_imagem=None):
        self.set_nome(nome)
        self.set_tags(tags)
        self.set_caminho_imagem(caminho_imagem)

    def set_nome(self, nome):
        self._nome = nome

    def set_tags(self, tags):
        self._tags = set(tags)

    def set_caminho_imagem(self, caminho_imagem):
        self._caminho_imagem = caminho_imagem

    @property
    def nome(self):
        return self._nome

    @property
    def tags(self):
        return set(self._tags)

    @property
    def caminho_imagem(self):
        return self._caminho_imagem

    def __str__(self):
        return f"{self._nome}, tags: {self._tags}, imagem: {self._caminho_imagem}"

    def contem(self, outra):
        return outra._tags.issubset(self._tags)
