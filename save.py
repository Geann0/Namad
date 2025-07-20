import random
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import unicodedata

button_style = {
    'bg': '#000000',  # Black background without transparency
    'fg': '#FFFFFF',
    'activebackground': '#3D6AFF',
    'font': ('Menlo', 10, 'bold'),
    'relief': tk.FLAT,
    'bd': 0,
}

hover_style = {
    'background': '#3D6AFF',
}

def on_enter(e):
    e.widget['bg'] = hover_style['background']

def on_leave(e):
    e.widget['bg'] = button_style['bg']

class HistoricalFigureGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Adivinhe o Personaggio Histórico")
        self.master.geometry("800x600")

        self.figures = self.load_figures_from_file("historical_figures.json")
        self.advantages = {
            "dicas": {"quantidade": 3, "custo": 5},
            "pulo": {"quantidade": 2, "custo": 10},
            "pesquisa": {"quantidade": 1, "custo": 20}
        }

        self.current_figure = {}
        self.score = 0
        self.money = 0
        self.lives = 3
        self.hints_used = 0
        self.skips_used = 0
        self.research_used = 0
        self.game_over = False

        self.intro_label = tk.Label(
            master, text="Bem-vindo ao Adivinhe o Personagem Histórico!\nTente adivinhar o personagem com base no fato histórico."
        )
        self.intro_label.pack(pady=10)

        self.fact_label = tk.Label(master, text="", wraplength=600, justify="left", width=80)
        self.fact_label.pack(pady=10)

        self.label = tk.Label(master, text="Digite o nome do personagem:")
        self.label.pack(pady=5)

        self.entry = tk.Entry(master)
        self.entry.pack(pady=5)

        self.button = tk.Button(master, text="Adivinhar", command=self.check_guess, **button_style)
        self.button.pack(pady=10)
        self.button.bind("<Enter>", on_enter)
        self.button.bind("<Leave>", on_leave)

        # Adicionando botões de vantagens
        self.hint_button = tk.Button(master, text="Dica", command=self.use_hint, **button_style)
        self.hint_button.pack(side=tk.LEFT, padx=10)
        self.hint_button.bind("<Enter>", on_enter)
        self.hint_button.bind("<Leave>", on_leave)

        self.skip_button = tk.Button(master, text="Pular", command=self.use_skip, **button_style)
        self.skip_button.pack(side=tk.LEFT, padx=10)
        self.skip_button.bind("<Enter>", on_enter)
        self.skip_button.bind("<Leave>", on_leave)

        self.research_button = tk.Button(master, text="Pesquisar", command=self.use_research, **button_style)
        self.research_button.pack(side=tk.LEFT, padx=10)
        self.research_button.bind("<Enter>", on_enter)
        self.research_button.bind("<Leave>", on_leave)

        # Adicionando botão da loja no canto superior direito
        self.shop_button = tk.Button(master, text="Loja", command=self.open_shop, **button_style)
        self.shop_button.pack(side=tk.RIGHT, padx=10)
        self.shop_button.bind("<Enter>", on_enter)
        self.shop_button.bind("<Leave>", on_leave)

        self.score_label = tk.Label(master, text="Pontuação: 0")
        self.score_label.pack(pady=5)

        self.record_label = tk.Label(master, text=f"Recorde: {self.load_record()} | Dinheiro: {self.money}")
        self.record_label.pack(pady=5)

        self.advantage_label = tk.Label(master, text="Vantagens disponíveis: Dicas(3), Pulo(2), Pesquisa(1)")
        self.advantage_label.pack(pady=5)

        self.new_game()

        # Adiciona um evento para a tecla "Enter"
        self.master.bind("<Return>", lambda event: self.check_guess())

    def load_figures_from_file(self, filename):
        try:
            with open(filename, "r") as file:
                figures = json.load(file)
            return figures
        except (json.JSONDecodeError, FileNotFoundError):
            messagebox.showerror("Erro", "Arquivo de figuras históricas não encontrado ou formato inválido.")
            return []

    def normalize_string(self, s):
        # Normaliza a string removendo acentos e convertendo para minúsculas
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8').lower()

    def new_game(self):
        self.game_over = False
        random.shuffle(self.figures)
        self.current_figure = self.figures[0]
        self.fact_label.config(text=self.current_figure["fact"])
        self.update_score()

    def update_score(self):
        self.score_label.config(text=f"Pontuação: {self.score}")

    def update_record(self):
        record_text = self.record_label.cget("text").split("|")[0].split(":")[1].strip()
        current_record = int(record_text) if record_text != "Nenhum" else 0

        if self.score > current_record:
            self.record_label.config(text=f"Recorde: {self.score} | Dinheiro: {self.money}")

    def update_advantages_label(self):
        hints_left = self.advantages["dicas"]["quantidade"]
        skips_left = self.advantages["pulo"]["quantidade"]
        research_left = self.advantages["pesquisa"]["quantidade"]

        self.advantage_label.config(text=f"Vantagens disponíveis: Dicas({hints_left}), Pulo({skips_left}), Pesquisa({research_left})")

    def use_hint(self):
        if self.advantages["dicas"]["quantidade"] > 0:
            self.hints_used += 1
            self.advantages["dicas"]["quantidade"] -= 1
            self.update_advantages_label()

            hint = self.current_figure["name"][:self.hints_used]
            messagebox.showinfo("Dica", f"Dica: {hint}{'_' * (len(self.current_figure['name']) - self.hints_used)}")
        else:
            messagebox.showinfo("Vantagem Indisponível", "Você não possui mais dicas disponíveis.")

    def use_skip(self):
        if self.advantages["pulo"]["quantidade"] > 0:
            self.skips_used += 1
            self.advantages["pulo"]["quantidade"] -= 1
            self.update_advantages_label()
            self.new_game()
        else:
            messagebox.showinfo("Vantagem Indisponível", "Você não possui mais pulos disponíveis.")

    def use_research(self):
        if self.advantages["pesquisa"]["quantidade"] > 0:
            research_result = simpledialog.askstring("Pesquisa", "Digite o nome do personagem:")
            research_result = self.normalize_string(research_result.strip())
            correct_name = self.normalize_string(self.current_figure["name"])

            if research_result == correct_name:
                messagebox.showinfo("Pesquisa", "Pesquisa bem-sucedida! Pontuação extra concedida.")
                self.research_used += 1
                self.advantages["pesquisa"]["quantidade"] -= 1
                self.update_advantages_label()
                self.score += 5  # Pontuação extra por pesquisa correta
                self.update_score()
                self.new_game()
            else:
                messagebox.showinfo("Pesquisa", "Pesquisa sem sucesso. Continue tentando!")
                self.research_used += 1
                self.advantages["pesquisa"]["quantidade"] -= 1
                self.update_advantages_label()
        else:
            messagebox.showinfo("Vantagem Indisponível", "Você não possui mais pesquisas disponíveis.")

    def open_shop(self):
        if not self.game_over:
            shop_window = tk.Toplevel(self.master)
            shop_window.title("Loja")
            shop_window.geometry("300x200")

            shop_label = tk.Label(
                shop_window, text=f"Bem-vindo à Loja!\nVocê possui {self.money} dinheiro."
            )
            shop_label.pack(pady=10)

            hints_button = tk.Button(
                shop_window, text=f"Dicas (Custo: {self.advantages['dicas']['custo']} dinheiro)", command=self.buy_hint
            )
            hints_button.pack(pady=5)

            skips_button = tk.Button(
                shop_window, text=f"Pulo (Custo: {self.advantages['pulo']['custo']} dinheiro)", command=self.buy_skip
            )
            skips_button.pack(pady=5)

            research_button = tk.Button(
                shop_window, text=f"Pesquisa (Custo: {self.advantages['pesquisa']['custo']} dinheiro)", command=self.buy_research
            )
            research_button.pack(pady=5)

            close_button = tk.Button(shop_window, text="Fechar", command=shop_window.destroy)
            close_button.pack(pady=10)
        else:
            messagebox.showinfo("Jogo Finalizado", "O jogo está finalizado. Inicie um novo jogo.")

    def buy_hint(self):
        self.buy_item("dicas")

    def buy_skip(self):
        self.buy_item("pulo")

    def buy_research(self):
        self.buy_item("pesquisa")

    def buy_item(self, item):
        if not self.game_over:
            if self.money >= self.advantages[item]["custo"]:
                self.advantages[item]["quantidade"] += 1
                self.money -= self.advantages[item]["custo"]
                self.update_advantages_label()
                messagebox.showinfo("Compra realizada", f"Compra de {item.capitalize()} realizada com sucesso!")
            else:
                messagebox.showinfo("Dinheiro insuficiente", f"Dinheiro insuficiente para comprar {item.capitalize()}.")
        else:
            messagebox.showinfo("Jogo Finalizado", "O jogo está finalizado. Inicie um novo jogo.")

    def check_guess(self, event=None):
        if not self.game_over:
            guessed_name = self.normalize_string(self.entry.get().strip())
            correct_name = self.normalize_string(self.current_figure["name"])

            if guessed_name == "":
                messagebox.showinfo("Campo Vazio", "Por favor, digite o nome do personagem antes de adivinhar.")
                return

            if guessed_name == correct_name:
                messagebox.showinfo("Adivinha Correta!", f"Parabéns! Você acertou.\n\n{correct_name}: {self.current_figure['fact']}")
                self.score += self.calculate_score()
                self.money += 10  # Adiciona dinheiro por adivinhação correta
            else:
                messagebox.showinfo("Adivinha Incorreta!", f"Infelizmente, sua resposta está incorreta.\n\n{correct_name}: {self.current_figure['fact']}")
                self.lives -= 1
                if self.lives == 0:
                    self.end_game()

            self.update_record()
            self.update_score()
            self.update_advantages_label()
            self.entry.delete(0, tk.END)  # Limpa a caixa de texto
            self.new_game()
        else:
            messagebox.showinfo("Jogo Finalizado", "O jogo está finalizado. Inicie um novo jogo.")

    def end_game(self):
        self.game_over = True
        messagebox.showinfo("Fim de Jogo", f"Você perdeu. Sua pontuação final foi: {self.score}")
        if self.score > 0:
            self.save_game()
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.hints_used = 0
        self.skips_used = 0
        self.research_used = 0
        self.game_over = False
        self.new_game()

    def save_game(self):
        try:
            with open("game_save.json", "w") as save_file:
                save_data = {
                    "record": max(self.score, self.load_record()),
                    "money": self.money
                }
                json.dump(save_data, save_file)
        except Exception as e:
            print(f"Erro ao salvar o jogo: {e}")

    def load_record(self):
        try:
            with open("game_save.json", "r") as save_file:
                save_data = json.load(save_file)
                return save_data.get("record", 0)
        except Exception as e:
            return 0

    def calculate_score(self):
        # Ajusta a pontuação com base na dificuldade percebida do personagem
        # Personagens mais difíceis têm pontuações mais altas
        difficulty_factor = 1.0 + len(self.current_figure["name"]) / 10.0
        return int(10 * difficulty_factor)

if __name__ == "__main__":
    root = tk.Tk()
    game = HistoricalFigureGame(root)
    root.mainloop()