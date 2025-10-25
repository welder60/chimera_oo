# Chimera OO

Sistema simples em Python para gerenciar entidades fictícias e suas relações de tags.

## Visão geral

<img width="447" height="430" alt="Diagrama UML" src="https://github.com/user-attachments/assets/cf11429d-863e-4101-84a1-0b28b34762db" />

O projeto define duas classes principais:

- `Entidade`: representa um ser com um nome e um conjunto de tags.
- `GerenciadorEntidades`: armazena instâncias de `Entidade`, permitindo:
  - adicionar entidades manualmente;
  - carregar entidades a partir de um arquivo CSV;
  - recuperar entidades pelo nome;
  - cruzar entidades com base nas tags;
  - descobrir evoluções (superconjuntos de tags) e derivações (subconjuntos de tags).

A pasta `package/` contém as implementações das classes, enquanto os arquivos `test_*.py` trazem testes unitários demonstrando os principais cenários de uso.

## Requisitos

- Python 3.8 ou superior

## Executando a aplicação desktop

A interface principal do projeto é uma aplicação desktop construída com Tkinter. Para executá-la, utilize:

```bash
python app.py
```

Isso abrirá a janela "Laboratório de Quimeras", permitindo selecionar criaturas, realizar fusões e acompanhar novas descobertas.

## Executando os testes

Os testes unitários validam o comportamento das classes. Execute-os com:

```bash
python -m unittest
```

Isso irá executar todos os testes encontrados nos arquivos `test_entidade.py` e `test_gerenciador_entidades.py`.

## Exemplos rápidos

```python
from package.entidade import Entidade
from package.gerenciador_entidades import GerenciadorEntidades

# Cria algumas entidades
humano = Entidade("Humano", ["HUMANOIDE"])
touro = Entidade("Touro", ["CHIFRES"])
minotauro = Entidade("Minotauro", ["HUMANOIDE", "CHIFRES"])

# Inicia o gerenciador e adiciona entidades
ge = GerenciadorEntidades()
for entidade in (humano, touro, minotauro):
    ge.adicionar(entidade)

# Descobre derivações e evoluções do Minotauro
print([e._nome for e in ge.derivacoes(minotauro)])
print([e._nome for e in ge.evolucoes(minotauro)])
```

## Licença

Este projeto está licenciado sob os termos da [Licença MIT](LICENSE).
