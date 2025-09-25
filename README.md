# Chimera OO

Chimera OO é uma biblioteca simples para trabalhar com "entidades" descritas por um nome e um conjunto de tags.
O projeto demonstra como criar, armazenar, relacionar e consultar essas entidades seguindo um estilo orientado a
objetos em Python.

## Estrutura do projeto

```
package/
├── entidade.py               # Define a classe `Entidade`
├── gerenciador_entidades.py  # Define a classe `GerenciadorEntidades`
└── __init__.py               # Expõe as classes principais do pacote
```

Os testes automatizados estão nos arquivos `test_entidade.py` e `test_gerenciador_entidades.py` na raiz do repositório.

## Pré-requisitos

- Python 3.12 ou superior.
- `pip` para instalar dependências opcionais de desenvolvimento.

## Instalação e uso

Clone o repositório e, caso queira trabalhar em um ambiente isolado, crie e ative um ambiente virtual.

```bash
python -m venv .venv
source .venv/bin/activate  # No Windows use `.venv\\Scripts\\activate`
```

Em seguida instale as dependências necessárias (caso existam) e utilize o pacote diretamente no Python.

```bash
pip install -e .
```

Exemplo rápido de uso:

```python
from package import Entidade, GerenciadorEntidades

gerenciador = GerenciadorEntidades()

drago = Entidade("Dragão", {"fogo", "voador"})
fenix = Entidade("Fênix", {"fogo", "renascimento"})

for entidade in (drago, fenix):
    gerenciador.adicionar(entidade)

print(gerenciador.evolucoes(drago))
```

## Importação a partir de CSV

O método `GerenciadorEntidades.carregar_csv` permite carregar entidades a partir de um arquivo CSV.
O arquivo precisa conter as colunas `nome` e `tags`, onde `tags` deve ser uma lista separada por vírgulas.

```csv
nome,tags
Dragão,"fogo, voador"
Fênix,"fogo, renascimento"
```

```python
gerenciador = GerenciadorEntidades()
gerenciador.carregar_csv("dados_entidades.csv")
```

## Executando os testes

Os testes de unidade utilizam `pytest`. Para executá-los:

```bash
pytest
```

O comando acima executará todos os testes localizados nos arquivos `test_entidade.py` e `test_gerenciador_entidades.py`.
