import os
import tempfile
import unittest

from package.jogador import Jogador


class TestJogador(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_registra_descobertas(self):
        jogador = Jogador("Alice", arquivo_progresso=self.temp_file.name)
        self.assertEqual(jogador.quantidade_descobertas, 0)

        jogador.registrar_fusao("Minotauro")
        self.assertEqual(jogador.quantidade_descobertas, 1)
        self.assertIn("Minotauro", jogador.criaturas_descobertas)

    def test_persistencia_pickle(self):
        jogador = Jogador("Bob", arquivo_progresso=self.temp_file.name)
        jogador.registrar_fusao("Sereia")

        novo_jogador = Jogador("Bob", arquivo_progresso=self.temp_file.name)
        self.assertEqual(novo_jogador.quantidade_descobertas, 1)
        self.assertIn("Sereia", novo_jogador.criaturas_descobertas)


if __name__ == "__main__":
    unittest.main()
