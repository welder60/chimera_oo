# Chimera OO

Sistema simples em Python para gerenciar entidades fictícias e suas relações de tags.

## Visão geral

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

## Instalação do ambiente

Crie e ative um ambiente virtual (opcional, mas recomendado) e instale as dependências.

```bash
python -m venv .venv
source .venv/bin/activate  # No Windows use: .venv\Scripts\activate
pip install -r requirements.txt  # se existir um arquivo de dependências
```

> O projeto não possui dependências externas além da biblioteca padrão, logo o arquivo `requirements.txt` é opcional.

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
