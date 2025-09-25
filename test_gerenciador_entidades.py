import unittest
import tempfile
import os
from package.entidade import Entidade
from package.gerenciador_entidades import GerenciadorEntidades


class TestGerenciadorEntidades(unittest.TestCase):
    """
    Testes para validar o comportamento do GerenciadorEntidades
    e suas interações com a classe Entidade.
    """

    def setUp(self):
        """
        Executa antes de cada teste.
        Cria algumas entidades iniciais e popula o gerenciador.
        """
        # Entidades básicas
        self.humano = Entidade("Humano", ["HUMANOIDE"])
        self.touro = Entidade("Touro", ["CHIFRES"])
        self.minotauro = Entidade("Minotauro", ["HUMANOIDE", "CHIFRES"])
        self.minotauro_de_ferro = Entidade("Minotauro de Ferro", ["HUMANOIDE", "CHIFRES", "FERRO"])

        # Gerenciador inicializado
        self.gerenciador_entidades = GerenciadorEntidades()

        # Adiciona entidades iniciais
        self.gerenciador_entidades.adicionar(self.humano)
        self.gerenciador_entidades.adicionar(self.touro)
        self.gerenciador_entidades.adicionar(self.minotauro)
        self.gerenciador_entidades.adicionar(self.minotauro_de_ferro)

        # Adiciona algumas extras
        self.gerenciador_entidades.adicionar(Entidade("Peixe", ["AQUATICO"]))
        self.gerenciador_entidades.adicionar(Entidade("Sereia", ["HUMANOIDE", "AQUATICO"]))
        self.gerenciador_entidades.adicionar(Entidade("Ferro", ["FERRO"]))

    def test_adicionar(self):
        """
        Testa se uma entidade é corretamente adicionada ao gerenciador.
        """
        self.gerenciador_entidades.adicionar(self.touro)
        self.assertIn(self.touro, self.gerenciador_entidades._entidades)

    def test_get(self):
        """
        Testa se é possível recuperar uma entidade pelo nome.
        """
        self.gerenciador_entidades.adicionar(Entidade("Dragão", ["ASAS", "FOGO", "REPTIL"]))
        resultado = self.gerenciador_entidades.get(["Dragão"])
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]._nome, "Dragão")

    def test_carregar_csv(self):
        """
        Testa se o carregamento a partir de um CSV adiciona
        a entidade esperada ao gerenciador.
        """
        conteudo = "nome,tags\nDragão,FOGO,VOADOR\n"
        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as tmp:
            tmp.write(conteudo)
            tmp_path = tmp.name

        tamanho_anterior = len(self.gerenciador_entidades._entidades)
        self.gerenciador_entidades.carregar_csv(tmp_path)
        os.remove(tmp_path)

        # Verifica se aumentou a quantidade de entidades
        self.assertEqual(len(self.gerenciador_entidades._entidades), tamanho_anterior + 1)

        # Verifica se o Dragão foi adicionado corretamente
        dragao_adicionado = self.gerenciador_entidades.get(["Dragão"])[0]
        self.assertEqual(dragao_adicionado._nome, "Dragão")
        self.assertIn("FOGO", dragao_adicionado._tags)

    def test_cruzar(self):
        """
        Testa se o cruzamento de Humano e Touro gera Minotauro
        e não inclui entidades com tags extras.
        """
        resultado = self.gerenciador_entidades.cruzar(
            self.gerenciador_entidades.get(["Humano", "Touro"])
        )
        # Minotauro deve aparecer no resultado
        self.assertIn(self.gerenciador_entidades.get(["Minotauro"])[0], resultado)
        # Minotauro de Ferro não deve aparecer (tem tag extra)
        self.assertNotIn(self.gerenciador_entidades.get(["Minotauro de Ferro"])[0], resultado)

    def test_evolucoes_derivacoes(self):
        """
        Testa se as relações de evolução e derivação funcionam:
        - Minotauro de Ferro é uma evolução do Minotauro
        - Humano e Touro são derivações do Minotauro
        """
        # Relação de contenção entre tags
        self.assertTrue(self.minotauro.contem(self.humano))

        # Evoluções: entidades que possuem todas as tags do minotauro + extras
        evolucoes = self.gerenciador_entidades.evolucoes(self.minotauro)
        self.assertIn(self.minotauro_de_ferro, evolucoes)

        # Derivações: entidades que têm subconjunto das tags do minotauro
        derivacoes = self.gerenciador_entidades.derivacoes(self.minotauro)
        self.assertIn(self.humano, derivacoes)
        self.assertIn(self.touro, derivacoes)


if __name__ == "__main__":
    unittest.main()
