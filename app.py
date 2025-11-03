"""Aplicação desktop para o Laboratório de Quimeras."""

from __future__ import annotations

from PIL import Image, ImageTk

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import json
import random

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


FUSAO_CUSTO_CREDITOS = 1


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
        self.contador_var = tk.StringVar()
        self.creditos_var = tk.StringVar()

        self.pergunta_var = tk.StringVar()
        self.alternativa_var = tk.StringVar()
        self.quiz_feedback_var = tk.StringVar()
        self.pergunta_respondida = False

        self.questoes = self._carregar_questoes()
        self.questao_atual: Dict[str, object] | None = None

        style = ttk.Style(self)
        style.configure("Card.TFrame", background="#f0f0f0")
        style.configure("Selecionado.TFrame", background="#c1e1c1")

        self._montar_interface()
        self._atualizar_descobertas()
        self._atualizar_creditos()
        self._sortear_pergunta()

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
            padding=(0, 8, 0, 12),
        )
        descricao.pack(fill=tk.X)

        contador_lbl = ttk.Label(
            main_frame,
            textvariable=self.contador_var,
            font=("Helvetica", 11, "bold"),
        )
        contador_lbl.pack(anchor=tk.W)

        creditos_lbl = ttk.Label(
            main_frame,
            textvariable=self.creditos_var,
            font=("Helvetica", 11, "bold"),
            foreground="#1f3c88",
            padding=(0, 0, 0, 12),
        )
        creditos_lbl.pack(anchor=tk.W)

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        fusao_tab = ttk.Frame(notebook)
        notebook.add(fusao_tab, text="Laboratório de Fusão")

        quiz_tab = ttk.Frame(notebook)
        notebook.add(quiz_tab, text="Desafios OO")

        selecao_frame = ttk.Frame(fusao_tab)
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

        botoes_frame = ttk.Frame(fusao_tab, padding=(0, 12))
        botoes_frame.pack(fill=tk.X)

        fusao_btn = ttk.Button(
            botoes_frame, text="Realizar Fusão", command=self.realizar_fusao
        )
        fusao_btn.pack(side=tk.LEFT)

        limpar_btn = ttk.Button(
            botoes_frame, text="Limpar Seleção", command=self._limpar_selecao
        )
        limpar_btn.pack(side=tk.LEFT, padx=(8, 0))

        mensagem_lbl = ttk.Label(
            fusao_tab,
            textvariable=self.mensagem_var,
            foreground="#1f3c88",
            wraplength=600,
        )
        mensagem_lbl.pack(fill=tk.X, pady=(8, 0))

        novas_frame = ttk.LabelFrame(fusao_tab, text="Novas criaturas descobertas")
        novas_frame.pack(fill=tk.BOTH, expand=True, pady=(16, 0))

        canvas_novas = tk.Canvas(novas_frame, height=160)
        scrollbar_novas = ttk.Scrollbar(
            novas_frame, orient=tk.HORIZONTAL, command=canvas_novas.xview
        )
        scrollbar_novas.pack(side=tk.BOTTOM, fill=tk.X)

        canvas_novas.configure(xscrollcommand=scrollbar_novas.set)
        canvas_novas.pack(fill=tk.BOTH, expand=True)

        self.novas_frame = ttk.Frame(canvas_novas)
        canvas_novas.create_window((0, 0), window=self.novas_frame, anchor="nw")

        self.novas_frame.bind(
            "<Configure>",
            lambda e: canvas_novas.configure(scrollregion=canvas_novas.bbox("all")),
        )

        quiz_instrucao = ttk.Label(
            quiz_tab,
            text=(
                "Responda às perguntas para ganhar créditos e liberar novas tentativas "
                "de fusão. Cada resposta correta vale 1 crédito."
            ),
            wraplength=520,
            padding=(0, 12, 0, 8),
        )
        quiz_instrucao.pack(anchor=tk.W, fill=tk.X)

        pergunta_lbl = ttk.Label(
            quiz_tab,
            textvariable=self.pergunta_var,
            wraplength=520,
            font=("Helvetica", 12, "bold"),
        )
        pergunta_lbl.pack(anchor=tk.W, fill=tk.X)

        self.alternativas_frame = ttk.Frame(quiz_tab)
        self.alternativas_frame.pack(anchor=tk.W, fill=tk.X, pady=(8, 12))

        botoes_quiz = ttk.Frame(quiz_tab)
        botoes_quiz.pack(fill=tk.X, pady=(0, 12))

        responder_btn = ttk.Button(
            botoes_quiz, text="Responder", command=self._verificar_resposta
        )
        responder_btn.pack(side=tk.LEFT)

        proxima_btn = ttk.Button(
            botoes_quiz, text="Próxima pergunta", command=self._sortear_pergunta
        )
        proxima_btn.pack(side=tk.LEFT, padx=(8, 0))

        feedback_lbl = ttk.Label(
            quiz_tab,
            textvariable=self.quiz_feedback_var,
            wraplength=520,
            foreground="#1f3c88",
        )
        feedback_lbl.pack(anchor=tk.W, fill=tk.X)

    # ------------------------------------------------------------------
    # Lógica da aplicação
    # ------------------------------------------------------------------
    def realizar_fusao(self):
        selecionadas = list(self.criaturas_selecionadas)
        if len(selecionadas) < 2:
            self.mensagem_var.set(
                "Selecione pelo menos duas criaturas para realizar a fusão."
            )
            return

        if not self.jogador.tem_creditos(FUSAO_CUSTO_CREDITOS):
            self.mensagem_var.set(
                "Você precisa de créditos para realizar a fusão. Responda às "
                "perguntas na aba Desafios OO para ganhar créditos. É "
                f"necessário ao menos {FUSAO_CUSTO_CREDITOS} crédito."
            )
            self._mostrar_novas_criaturas([])
            return

        resultado = self._processar_fusao(selecionadas)
        self.mensagem_var.set(resultado.mensagem)

        if resultado.novas_criaturas:
            if not self.jogador.gastar_creditos(FUSAO_CUSTO_CREDITOS):
                self.mensagem_var.set(
                    "Não foi possível consumir créditos para realizar a fusão."
                )
                self._mostrar_novas_criaturas([])
                return
            self._atualizar_creditos()
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
        descobertas_validas = 0
        for nome in nomes:
            encontradas = self.gerenciador.get([nome])
            if not encontradas:
                continue
            entidade = encontradas[0]
            entidades.append(entidade)
            descobertas_validas += 1
            iid = self._criar_iid("descoberta", nome)
            imagem = self._obter_imagem(entidade)

        if entidades:
            self._incluir_criaturas_disponiveis(entidades)

        self._atualizar_contador(descobertas_validas)

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

    def _atualizar_creditos(self):
        self.creditos_var.set(
            f"Créditos disponíveis: {self.jogador.creditos}"
        )

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

    def _atualizar_contador(self, descobertas: int):
        total = len(self.gerenciador.listar_nomes())
        faltam = max(total - descobertas, 0)
        self.contador_var.set(
            f"Quimeras descobertas: {descobertas} de {total} (faltam {faltam})"
        )

    # ------------------------------------------------------------------
    # Sistema de perguntas e respostas
    # ------------------------------------------------------------------
    def _carregar_questoes(self) -> List[Dict[str, object]]:
        caminho = Path(__file__).parent / "assets" / "perguntas_oo.json"
        if not caminho.exists():
            return []
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except (json.JSONDecodeError, OSError):
            return []

        questoes_validas: List[Dict[str, object]] = []
        for questao in dados:
            if not isinstance(questao, dict):
                continue
            pergunta = questao.get("pergunta")
            alternativas = questao.get("alternativas")
            try:
                correta = int(questao.get("correta"))
            except (TypeError, ValueError):
                continue

            if not pergunta or not isinstance(alternativas, list) or len(alternativas) < 2:
                continue
            if not 0 <= correta < len(alternativas):
                continue

            questoes_validas.append(
                {
                    "pergunta": str(pergunta),
                    "alternativas": [str(opcao) for opcao in alternativas],
                    "correta": correta,
                }
            )
        return questoes_validas

    def _sortear_pergunta(self):
        if not getattr(self, "alternativas_frame", None):
            return

        if not self.questoes:
            self.questao_atual = None
            self.pergunta_var.set("Nenhuma pergunta disponível no momento.")
            self.quiz_feedback_var.set("")
            self._limpar_alternativas()
            self.pergunta_respondida = False
            return

        self.questao_atual = random.choice(self.questoes)
        self.pergunta_var.set(str(self.questao_atual["pergunta"]))
        self.quiz_feedback_var.set("")
        self.pergunta_respondida = False
        self.alternativa_var.set("")
        self._exibir_alternativas(self.questao_atual["alternativas"])

    def _exibir_alternativas(self, alternativas: Sequence[str]):
        self._limpar_alternativas()
        for indice, alternativa in enumerate(alternativas):
            ttk.Radiobutton(
                self.alternativas_frame,
                text=alternativa,
                value=str(indice),
                variable=self.alternativa_var,
            ).pack(anchor=tk.W, pady=2)

    def _limpar_alternativas(self):
        if not getattr(self, "alternativas_frame", None):
            return
        for widget in self.alternativas_frame.winfo_children():
            widget.destroy()
        self.alternativa_var.set("")

    def _verificar_resposta(self):
        if not self.questao_atual:
            self.quiz_feedback_var.set("Nenhuma pergunta disponível no momento.")
            return

        if self.pergunta_respondida:
            self.quiz_feedback_var.set(
                "Você já respondeu esta pergunta. Avance para a próxima."
            )
            return

        resposta = self.alternativa_var.get()
        if resposta == "":
            self.quiz_feedback_var.set("Selecione uma alternativa antes de responder.")
            return

        correta = str(self.questao_atual["correta"])
        if resposta == correta:
            self.pergunta_respondida = True
            self.jogador.adicionar_creditos(1)
            self.quiz_feedback_var.set(
                "Resposta correta! Você ganhou 1 crédito."
            )
            self._atualizar_creditos()
        else:
            self.quiz_feedback_var.set("Resposta incorreta. Tente novamente.")

if __name__ == "__main__":  # pragma: no cover
    app = ChimeraDesktopApp()
    app.mainloop()
