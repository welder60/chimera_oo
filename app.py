"""Aplicação desktop para o Laboratório de Quimeras."""

from __future__ import annotations

from PIL import Image, ImageTk

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
        self.title("Chimera OO")
        self.geometry("720x480")
        self.minsize(640, 420)

        self.gerenciador = GerenciadorEntidades()
        self.jogador = Jogador(jogador_padrao)

        self._imagem_cache: Dict[str, tk.PhotoImage] = {}

        self.mensagem_var = tk.StringVar()
        self.novas_var = tk.StringVar()

        style = ttk.Style(self)
        style.configure("Card.TFrame", background="#f0f0f0")
        style.configure("Selecionado.TFrame", background="#c1e1c1")

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
            text="Chimera OO",
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

        # --- Novo container de seleção em grade ---
        selecao_frame = ttk.Frame(main_frame)
        selecao_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(selecao_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            selecao_frame, orient=tk.VERTICAL, command=self.canvas.yview
        )
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.grid_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")

        self.grid_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.criaturas_widgets: Dict[str, ttk.Frame] = {}
        self.criaturas_selecionadas: set[str] = set()

        self._carregar_criaturas_iniciais()

        botoes_frame = ttk.Frame(main_frame, padding=(0, 12))
        botoes_frame.pack(fill=tk.X)

        fusao_btn = ttk.Button(botoes_frame, text="Realizar Fusão", command=self.realizar_fusao)
        fusao_btn.pack(side=tk.LEFT)

        limpar_btn = ttk.Button(botoes_frame, text="Limpar Seleção", command=self._limpar_selecao)
        limpar_btn.pack(side=tk.LEFT, padx=(8, 0))

        mensagem_lbl = ttk.Label(main_frame, textvariable=self.mensagem_var, foreground="#1f3c88", wraplength=600)
        mensagem_lbl.pack(fill=tk.X, pady=(8, 0))

        novas_frame = ttk.LabelFrame(main_frame, text="Novas criaturas descobertas")
        novas_frame.pack(fill=tk.X, pady=(16, 0))

        novas_frame = ttk.LabelFrame(main_frame, text="Novas criaturas descobertas")
        novas_frame.pack(fill=tk.BOTH, expand=True, pady=(16, 0))

        # Frame com rolagem
        canvas_novas = tk.Canvas(novas_frame, height=160)
        scrollbar_novas = ttk.Scrollbar(novas_frame, orient=tk.HORIZONTAL, command=canvas_novas.xview)
        scrollbar_novas.pack(side=tk.BOTTOM, fill=tk.X)

        canvas_novas.configure(xscrollcommand=scrollbar_novas.set)
        canvas_novas.pack(fill=tk.BOTH, expand=True)

        self.novas_frame = ttk.Frame(canvas_novas)
        canvas_novas.create_window((0, 0), window=self.novas_frame, anchor="nw")

        self.novas_frame.bind(
            "<Configure>", lambda e: canvas_novas.configure(scrollregion=canvas_novas.bbox("all"))
        )

    # ------------------------------------------------------------------
    # Lógica da aplicação
    # ------------------------------------------------------------------
    def realizar_fusao(self):
        selecionadas = list(self.criaturas_selecionadas)
        resultado = self._processar_fusao(selecionadas)
        self.mensagem_var.set(resultado.mensagem)

        if resultado.novas_criaturas:
            self._incluir_criaturas_disponiveis(resultado.novas_criaturas)
            self._mostrar_novas_criaturas(resultado.novas_criaturas)
        else:
            self._mostrar_novas_criaturas([])

        self._atualizar_descobertas()
        self._limpar_selecao()

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

        entidades: List[Entidade] = []
        for nome in nomes:
            encontradas = self.gerenciador.get([nome])
            if not encontradas:
                continue
            entidade = encontradas[0]
            entidades.append(entidade)
            iid = self._criar_iid("descoberta", nome)
            imagem = self._obter_imagem(entidade)
            
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
        self._renderizar_criaturas()
        
    def _incluir_criaturas_disponiveis(
        self, entidades: Sequence[Entidade]
    ):
        for entidade in entidades:
            self._adicionar_criatura_disponivel(entidade)
        self._renderizar_criaturas()


    def _adicionar_criatura_disponivel(self, entidade: Entidade):
        nome = entidade._nome
        if nome in self.criaturas_widgets:
            return

        imagem = self._obter_imagem(entidade)

        frame = ttk.Frame(self.grid_frame, borderwidth=2, relief="flat")
        label_img = ttk.Label(frame, image=imagem)
        label_img.image = imagem
        label_img.pack()
        label_nome = ttk.Label(frame, text=nome)
        label_nome.pack()

        def toggle_selecao(event=None, nome=nome, frame=frame):
            if nome in self.criaturas_selecionadas:
                self.criaturas_selecionadas.remove(nome)
                frame.config(style="Card.TFrame")
            else:
                self.criaturas_selecionadas.add(nome)
                frame.config(style="Selecionado.TFrame")

        frame.bind("<Button-1>", toggle_selecao)
        label_img.bind("<Button-1>", toggle_selecao)
        label_nome.bind("<Button-1>", toggle_selecao)

        self.criaturas_widgets[nome] = frame
    def _mostrar_novas_criaturas(self, criaturas: Sequence[Entidade]):
        # Limpa o conteúdo anterior
        for widget in self.novas_frame.winfo_children():
            widget.destroy()

        if not criaturas:
            ttk.Label(
                self.novas_frame,
                text="Nenhuma nova criatura foi descoberta desta vez.",
                foreground="#888",
            ).pack()
            return

        colunas = 4
        for i, entidade in enumerate(criaturas):
            nome = entidade._nome
            imagem = self._obter_imagem(entidade)

            frame = ttk.Frame(self.novas_frame, borderwidth=1, relief="solid", padding=4)
            label_img = ttk.Label(frame, image=imagem)
            label_img.image = imagem
            label_img.pack()
            ttk.Label(frame, text=nome).pack()

            frame.grid(row=i // colunas, column=i % colunas, padx=8, pady=8)

    def _obter_imagem(self, entidade: Entidade):
        caminho = entidade.caminho_imagem
        if not caminho:
            return None

        caminho_relativo = Path(caminho)
        if not caminho_relativo.is_absolute():
            caminho_relativo = Path(__file__).parent / caminho_relativo

        chave_cache = str(caminho_relativo.resolve())
        if chave_cache not in self._imagem_cache and caminho_relativo.exists():
            imagem = Image.open(caminho_relativo)
            imagem = imagem.resize((80, 80), Image.LANCZOS)
            self._imagem_cache[chave_cache] = ImageTk.PhotoImage(imagem)

        return self._imagem_cache.get(chave_cache)

    def _renderizar_criaturas(self):
        # Remove widgets visuais antigos, mas não destrói os frames guardados
        for widget in self.grid_frame.winfo_children():
            widget.grid_forget()

        colunas = 6
        for i, (nome, frame) in enumerate(sorted(self.criaturas_widgets.items())):
            frame.grid(row=i // colunas, column=i % colunas, padx=8, pady=8)

    def _limpar_selecao(self):
        for nome in list(self.criaturas_selecionadas):
            frame = self.criaturas_widgets[nome]
            frame.config(style="Card.TFrame")
        self.criaturas_selecionadas.clear()

if __name__ == "__main__":  # pragma: no cover
    app = ChimeraDesktopApp()
    app.mainloop()
