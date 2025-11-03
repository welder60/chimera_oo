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
        self.assertEqual(jogador.creditos, 0)

        jogador.registrar_fusao("Minotauro")
        self.assertEqual(jogador.quantidade_descobertas, 1)
        self.assertIn("Minotauro", jogador.criaturas_descobertas)

    def test_persistencia_pickle(self):
        jogador = Jogador("Bob", arquivo_progresso=self.temp_file.name)
        jogador.registrar_fusao("Sereia")
        jogador.adicionar_creditos(3)

        novo_jogador = Jogador("Bob", arquivo_progresso=self.temp_file.name)
        self.assertEqual(novo_jogador.quantidade_descobertas, 1)
        self.assertIn("Sereia", novo_jogador.criaturas_descobertas)
        self.assertEqual(novo_jogador.creditos, 3)

    def test_creditos_operacoes(self):
        jogador = Jogador("Carol", arquivo_progresso=self.temp_file.name)
        self.assertFalse(jogador.tem_creditos(1))

        jogador.adicionar_creditos(2)
        self.assertEqual(jogador.creditos, 2)
        self.assertTrue(jogador.tem_creditos(2))

        gasto = jogador.gastar_creditos(1)
        self.assertTrue(gasto)
        self.assertEqual(jogador.creditos, 1)

        gasto_insuficiente = jogador.gastar_creditos(5)
        self.assertFalse(gasto_insuficiente)
        self.assertEqual(jogador.creditos, 1)


if __name__ == "__main__":
    unittest.main()
