import unittest
from package.entidade import Entidade

class TestEntidade(unittest.TestCase):
    """
    Testes unitários para a classe Entidade.
    Verifica a criação, alteração de atributos, representação em string
    e a lógica de contenção de tags entre entidades.
    """

    def setUp(self):
        """
        Executa antes de cada teste.
        Cria duas entidades para reutilizar nos casos de teste:
        - Minotauro: possui HUMANOIDE e CHIFRES
        - Minotauro de Ferro: possui HUMANOIDE, CHIFRES e FERRO
        """
        self.minotauro = Entidade("Minotauro", ["HUMANOIDE", "CHIFRES"])
        self.minotauro_de_ferro = Entidade("Minotauro de Ferro", ["HUMANOIDE", "CHIFRES", "FERRO"])

    # --- Testes de criação e atributos básicos ---

    def test_criacao_entidade(self):
        """Deve criar entidade corretamente com nome e tags"""
        self.assertEqual(self.minotauro._nome, "Minotauro")
        self.assertIn("CHIFRES", self.minotauro._tags)
        self.assertEqual(len(self.minotauro._tags), 2)

    def test_set_nome(self):
        """Deve alterar o nome da entidade"""
        self.minotauro.set_nome("NovoNome")
        self.assertEqual(self.minotauro._nome, "NovoNome")

    def test_set_tags(self):
        """Deve alterar as tags da entidade"""
        self.minotauro.set_tags(["FORÇA", "AGILIDADE"])
        self.assertIn("FORÇA", self.minotauro._tags)
        self.assertIn("AGILIDADE", self.minotauro._tags)

    # --- Testes de comportamento especial ---

    def test_str(self):
        """__str__ deve retornar representação textual com nome e tags"""
        texto = str(self.minotauro)
        self.assertIn("Minotauro", texto)
        self.assertIn("CHIFRES", texto)

    # --- Testes de relacionamento (contem) ---

    def test_contem_true(self):
        """
        Minotauro de Ferro deve conter todas as tags do Minotauro,
        já que além de HUMANOIDE e CHIFRES ele tem FERRO.
        """
        self.assertTrue(self.minotauro_de_ferro.contem(self.minotauro))

    def test_contem_false(self):
        """
        Minotauro não contém todas as tags do Minotauro de Ferro,
        pois não possui a tag FERRO.
        """
        self.assertFalse(self.minotauro.contem(self.minotauro_de_ferro))


if __name__ == "__main__":
    unittest.main()
