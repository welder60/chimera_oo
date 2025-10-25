"""Aplicação desktop para o Laboratório de Quimeras."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import tkinter as tk
from tkinter import ttk

from package.gerenciador_entidades import Entidade, GerenciadorEntidades
from package.jogador import Jogador


def _ordenar_nomes(nomes: Iterable[str]) -> List[str]:
    return sorted(set(nomes))


@dataclass
class FusaResultado:
    novas_criaturas: List[Entidade]
    mensagem: str


class ChimeraDesktopApp(tk.Tk):
    """Interface gráfica principal da aplicação."""

    def __init__(self, jogador_padrao: str = "Convidado"):
        super().__init__()
        self.title("Laboratório de Quimeras")
        self.geometry("720x480")
        self.minsize(640, 420)

        self.gerenciador = GerenciadorEntidades()
        self.jogador = Jogador(jogador_padrao)

        self._imagem_cache: Dict[str, tk.PhotoImage] = {}

        self.mensagem_var = tk.StringVar()
        self.novas_var = tk.StringVar()

        self._montar_interface()
        self._atualizar_descobertas()

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------
    def _montar_interface(self):
        main_frame = ttk.Frame(self, padding=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        titulo = ttk.Label(
            main_frame,
            text="Bem-vindo ao Laboratório de Quimeras",
            font=("Helvetica", 16, "bold"),
        )
        titulo.pack(anchor=tk.W)

        descricao = ttk.Label(
            main_frame,
            text=(
                "Selecione pelo menos duas criaturas para tentar realizar uma "
                "fusão e descubra novas combinações!"
            ),
            wraplength=600,
            padding=(0, 8, 0, 16),
        )
        descricao.pack(fill=tk.X)

        selecao_frame = ttk.Frame(main_frame)
        selecao_frame.pack(fill=tk.BOTH, expand=True)

        self.lista_criaturas = ttk.Treeview(
            selecao_frame,
            show="tree",
            selectmode="extended",
            height=12,
        )
        self.lista_criaturas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.lista_criaturas.column("#0", anchor=tk.W, width=240)

        scrollbar = ttk.Scrollbar(
            selecao_frame, orient=tk.VERTICAL, command=self.lista_criaturas.yview
        )
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.lista_criaturas.config(yscrollcommand=scrollbar.set)

        self._carregar_criaturas_iniciais()

        botoes_frame = ttk.Frame(main_frame, padding=(0, 12))
        botoes_frame.pack(fill=tk.X)

        fusao_btn = ttk.Button(
            botoes_frame,
            text="Realizar Fusão",
            command=self.realizar_fusao,
        )
        fusao_btn.pack(side=tk.LEFT)

        limpar_btn = ttk.Button(
            botoes_frame,
            text="Limpar Seleção",
            command=self._limpar_selecao,
        )
        limpar_btn.pack(side=tk.LEFT, padx=(8, 0))

        mensagem_lbl = ttk.Label(
            main_frame,
            textvariable=self.mensagem_var,
            foreground="#1f3c88",
            wraplength=600,
        )
        mensagem_lbl.pack(fill=tk.X, pady=(8, 0))

        novas_frame = ttk.LabelFrame(main_frame, text="Novas criaturas descobertas")
        novas_frame.pack(fill=tk.X, pady=(16, 0))

        novas_lbl = ttk.Label(
            novas_frame,
            textvariable=self.novas_var,
            foreground="#0a8754",
            wraplength=600,
        )
        novas_lbl.pack(fill=tk.X, padx=8, pady=8)

        descobertas_frame = ttk.LabelFrame(
            main_frame, text="Códex de criaturas descobertas"
        )
        descobertas_frame.pack(fill=tk.BOTH, expand=True, pady=(16, 0))

        self.lista_descobertas = ttk.Treeview(
            descobertas_frame,
            show="tree",
            height=8,
        )
        self.lista_descobertas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.lista_descobertas.column("#0", anchor=tk.W)

    # ------------------------------------------------------------------
    # Lógica da aplicação
    # ------------------------------------------------------------------
    def realizar_fusao(self):
        selecionadas = [
            self.lista_criaturas.item(item, "text")
            for item in self.lista_criaturas.selection()
        ]

        resultado = self._processar_fusao(selecionadas)
        self.mensagem_var.set(resultado.mensagem)

        if resultado.novas_criaturas:
            nomes = ", ".join(entidade._nome for entidade in resultado.novas_criaturas)
            self.novas_var.set(nomes)
            self._incluir_criaturas_disponiveis(resultado.novas_criaturas)
        else:
            self.novas_var.set("Nenhuma nova criatura foi descoberta desta vez.")

        self._atualizar_descobertas()

    def _processar_fusao(self, selecionadas: List[str]) -> FusaResultado:
        if len(selecionadas) < 2:
            return FusaResultado([], "Selecione pelo menos duas criaturas para realizar a fusão.")

        entidades_escolhidas = self.gerenciador.get(selecionadas)
        if len(entidades_escolhidas) != len(selecionadas):
            return FusaResultado(
                [],
                "Algumas criaturas selecionadas não foram encontradas no gerenciador.",
            )

        novas_criaturas = self.gerenciador.cruzar(entidades_escolhidas)
        if not novas_criaturas:
            return FusaResultado(
                [], "Nenhuma combinação conhecida para as criaturas escolhidas."
            )

        for entidade in novas_criaturas:
            self.jogador.registrar_fusao(entidade._nome)

        return FusaResultado(
            novas_criaturas,
            "Fusão concluída! Novas criaturas foram adicionadas ao seu códex.",
        )

    def _atualizar_descobertas(self):
        nomes = _ordenar_nomes(self.jogador.criaturas_descobertas)
        for item in self.lista_descobertas.get_children():
            self.lista_descobertas.delete(item)

        entidades: List[Entidade] = []
        for nome in nomes:
            encontradas = self.gerenciador.get([nome])
            if not encontradas:
                continue
            entidade = encontradas[0]
            entidades.append(entidade)
            iid = self._criar_iid("descoberta", nome)
            imagem = self._obter_imagem(entidade)
            self.lista_descobertas.insert("", tk.END, iid=iid, text=nome, image=imagem)

        if entidades:
            self._incluir_criaturas_disponiveis(entidades)

    # ------------------------------------------------------------------
    # Métodos auxiliares
    # ------------------------------------------------------------------
    def _criar_iid(self, prefixo: str, nome: str) -> str:
        normalizado = nome.replace(" ", "_")
        return f"{prefixo}::{normalizado}"

    def _carregar_criaturas_iniciais(self):
        iniciais = self.gerenciador.listar_basicas()
        for entidade in iniciais:
            self._adicionar_criatura_disponivel(entidade)

    def _incluir_criaturas_disponiveis(
        self, entidades: Sequence[Entidade]
    ):
        for entidade in entidades:
            self._adicionar_criatura_disponivel(entidade)

    def _adicionar_criatura_disponivel(self, entidade: Entidade):
        nome = entidade._nome
        iid = self._criar_iid("criatura", nome)
        if self.lista_criaturas.exists(iid):
            return

        imagem = self._obter_imagem(entidade)
        nomes_existentes = [
            self.lista_criaturas.item(item, "text")
            for item in self.lista_criaturas.get_children()
        ]
        for indice, nome_existente in enumerate(nomes_existentes):
            if nome < nome_existente:
                self.lista_criaturas.insert(
                    "", indice, iid=iid, text=nome, image=imagem
                )
                break
        else:
            self.lista_criaturas.insert("", tk.END, iid=iid, text=nome, image=imagem)

    def _obter_imagem(self, entidade: Entidade):
        caminho = entidade.caminho_imagem
        if not caminho:
            return None

        caminho_relativo = Path(caminho)
        if not caminho_relativo.is_absolute():
            caminho_relativo = Path(__file__).parent / caminho_relativo

        chave_cache = str(caminho_relativo.resolve())
        if chave_cache not in self._imagem_cache and caminho_relativo.exists():
            self._imagem_cache[chave_cache] = tk.PhotoImage(file=str(caminho_relativo))
        return self._imagem_cache.get(chave_cache)

    def _limpar_selecao(self):
        selecionados = self.lista_criaturas.selection()
        if selecionados:
            self.lista_criaturas.selection_remove(selecionados)


if __name__ == "__main__":  # pragma: no cover
    app = ChimeraDesktopApp()
    app.mainloop()
