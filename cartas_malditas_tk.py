import tkinter as tk
from tkinter import messagebox
import random

MAX_HP = 20


class CartasMalditasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cartas Malditas - MVP Tkinter")

        # ESTADO DEL JUEGO
        self.deck = []
        self.room_cards = []
        self.carry_card = None
        self.player_hp = MAX_HP
        self.equipped_weapon = None
        self.score = 0
        self.skip_available = True

        # Seed de la run actual y RNG propio
        self.current_seed = None
        self.rng = random.Random()

        # UI SUPERIOR
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)

        self.hp_label = tk.Label(top_frame, text="HP: 20", width=15, height=3)
        self.hp_label.grid(row=0, column=0, padx=5)

        self.weapon_label = tk.Label(top_frame, text="Arma: (ninguna)", width=20, height=3)
        self.weapon_label.grid(row=0, column=1, padx=5)

        self.deck_label = tk.Label(top_frame, text="Mazo: 0", width=15, height=3)
        self.deck_label.grid(row=0, column=2, padx=5)

        self.score_label = tk.Label(top_frame, text="Puntuación: 0", width=20, height=3)
        self.score_label.grid(row=0, column=3, padx=5)

        # Label para mostrar la seed actual
        self.seed_label = tk.Label(top_frame, text="Seed: -", width=30)
        self.seed_label.grid(row=1, column=0, columnspan=4, pady=5)

        # UI CARTAS SALA
        room_frame = tk.Frame(root)
        room_frame.pack(pady=10)

        self.card_buttons = []
        for i in range(4):
            btn = tk.Button(
                room_frame,
                text="",
                width=18,
                height=3,
                state="disabled",
                command=lambda idx=i: self.on_card_button_pressed(idx)
            )
            btn.grid(row=0, column=i, padx=5)
            self.card_buttons.append(btn)

        # UI CARTA ARRASTRADA
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(pady=10)

        tk.Label(bottom_frame, text="Carta arrastrada:").grid(row=0, column=0, padx=5)

        self.carry_button = tk.Button(
            bottom_frame,
            text="Vacío",
            width=18,
            height=3,
            state="disabled"
        )
        self.carry_button.grid(row=0, column=1, padx=5)

        # CONTROL (botones de partida y salto de sala)
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)

        # Nueva partida con seed distinta
        self.new_run_button = tk.Button(
            control_frame,
            text="Nueva partida (seed aleatoria)",
            command=self.start_new_run
        )
        self.new_run_button.pack()

        # Repetir la misma seed
        self.repeat_seed_button = tk.Button(
            control_frame,
            text="Repetir run (misma seed)",
            command=self.restart_with_same_seed
        )
        self.repeat_seed_button.pack(pady=5)

        # Botón para saltar sala
        self.skip_button = tk.Button(
            control_frame,
            text="Saltar sala",
            command=self.skip_room
        )
        self.skip_button.pack(pady=5)

        # INICIAR PRIMERA PARTIDA
        self.start_new_run()

    # ============================================================
    #      SEED Y REINICIO
    # ============================================================

    def restart_with_same_seed(self):
        """Reinicia la partida reutilizando la misma seed de la run actual."""
        if self.current_seed is None:
            self.start_new_run()
        else:
            self.start_new_run(seed=self.current_seed)

    def start_new_run(self, seed=None):
        """Reinicia todo el estado del juego y genera (o reutiliza) la seed."""
        if seed is None:
            # Seed nueva aleatoria
            self.current_seed = random.randrange(1, 2**32)
        else:
            # Reutilizar seed específica
            self.current_seed = seed

        # RNG propio basado en la seed
        self.rng = random.Random(self.current_seed)

        # Reset de estado
        self.player_hp = MAX_HP
        self.equipped_weapon = None
        self.score = 0
        self.carry_card = None
        self.skip_available = True

        # Construir mazo y barajarlo con la seed
        self.build_deck()
        self.rng.shuffle(self.deck)

        # Habilitar botones de cartas
        for btn in self.card_buttons:
            btn.config(state="normal")

        # Generar primera sala
        self.next_room()
        self.update_ui()

    # ============================================================
    #      CONSTRUCCIÓN DEL MAZO
    # ============================================================

    def build_deck(self):
        """Mazo:
        - ♥ y ♦: 2–10
        - ♣ y ♠: 2–A (11=J,12=Q,13=K,14=A)
        """
        self.deck = []

        # 2–10 para todos los palos
        for value in range(2, 11):
            self.deck.append({"suit": "♥", "type": "potion", "value": value})
            self.deck.append({"suit": "♦", "type": "weapon", "value": value})
            self.deck.append({"suit": "♣", "type": "monster", "value": value})
            self.deck.append({"suit": "♠", "type": "monster", "value": value})

        # Figuras J/Q/K/A solo en ♣ y ♠ (monstruos fuertes)
        for value in range(11, 15):
            self.deck.append({"suit": "♣", "type": "monster", "value": value})
            self.deck.append({"suit": "♠", "type": "monster", "value": value})

    # ============================================================
    #      MECÁNICA DE SALTAR SALA
    # ============================================================

    def skip_room(self):
        """Salta la sala solo si está completa (4 cartas sin jugar)."""
        if not self.skip_available:
            return

        # Solo permitir salto si la sala tiene exactamente 4 cartas
        if len(self.room_cards) != 4:
            return

        # Mandamos la sala actual al final del mazo
        self.deck = self.room_cards + self.deck

        self.room_cards = []
        self.skip_available = False

        self.next_room()
        self.update_ui()

    # ============================================================
    #      MANEJO DE SALAS
    # ============================================================

    def next_room(self):
        self.room_cards = []

        if self.carry_card is not None:
            self.room_cards.append(self.carry_card)
            self.carry_card = None

        while len(self.room_cards) < 4 and self.deck:
            self.room_cards.append(self.deck.pop())

        # Si no hay cartas ni en sala ni en mazo → fin de partida
        if not self.room_cards and not self.deck:
            self.end_run(victory=self.player_hp > 0)
            return

        self.update_cards_ui()

    def update_cards_ui(self):
        for i, btn in enumerate(self.card_buttons):
            if i < len(self.room_cards):
                card = self.room_cards[i]
                btn.config(text=self.get_card_label(card), state="normal")
            else:
                btn.config(text="", state="disabled")

        if self.carry_card is not None:
            self.carry_button.config(text=self.get_card_label(self.carry_card))
        else:
            self.carry_button.config(text="Vacío")

        self.update_ui()

    def get_card_label(self, card):
        type_name = {
            "potion": "Poción",
            "weapon": "Arma",
            "monster": "Monstruo"
        }.get(card["type"], "?")

        v = card["value"]
        rank = {11: "J", 12: "Q", 13: "K", 14: "A"}.get(v, str(v))

        return f"{card['suit']} {rank} ({type_name})"

    # ============================================================
    #      LÓGICA DE COMBATE
    # ============================================================

    def on_card_button_pressed(self, index):
        if index >= len(self.room_cards):
            return

        card = self.room_cards[index]

        if card["type"] == "monster":
            self.play_monster(card)
        elif card["type"] == "potion":
            self.play_potion(card)
        elif card["type"] == "weapon":
            self.play_weapon(card)

        del self.room_cards[index]

        if self.player_hp <= 0:
            self.end_run(False)
            return

        # Si queda solo 1 carta en la sala → se arrastra y pasás de sala
        if len(self.room_cards) == 1:
            # Recarga del salto tras pasar sala normalmente
            self.skip_available = True

            self.carry_card = self.room_cards[0]
            self.room_cards = []
            self.next_room()
        else:
            self.update_cards_ui()

    def play_monster(self, card):
        """Combate con arma que se desgasta según el último monstruo válido."""
        monster_value = card["value"]

        if self.equipped_weapon is None:
            # Mano limpia
            self.player_hp -= monster_value
            self.score += 1
            return

        weapon_value = self.equipped_weapon["value"]
        weapon_limit = self.equipped_weapon["limit"]

        if monster_value <= weapon_limit:
            # El arma puede usarse contra este monstruo
            damage = monster_value - weapon_value
            if damage < 0:
                damage = 0
            self.player_hp -= damage

            # El arma ahora solo sirve contra monstruos menores a este
            self.equipped_weapon["limit"] = monster_value
        else:
            # El arma no sirve para este nivel → daño completo
            self.player_hp -= monster_value

        self.score += 1

    def play_potion(self, card):
        self.player_hp += card["value"]
        if self.player_hp > MAX_HP:
            self.player_hp = MAX_HP

    def play_weapon(self, card):
        """Equipa un arma con límite inicial muy alto (puede usarse contra cualquiera al inicio)."""
        self.equipped_weapon = {
            "suit": card["suit"],
            "type": "weapon",
            "value": card["value"],
            "limit": 15  # monstruos van de 2 a 14
        }

    # ============================================================
    #      UI & FIN DE PARTIDA
    # ============================================================

    def update_ui(self):
        self.hp_label.config(text=f"HP: {self.player_hp}")
        self.deck_label.config(text=f"Mazo: {len(self.deck)}")
        self.score_label.config(text=f"Puntuación: {self.score}")

        # Seed actual
        if self.current_seed is not None:
            self.seed_label.config(text=f"Seed: {self.current_seed}")
        else:
            self.seed_label.config(text="Seed: -")

        if self.equipped_weapon:
            if self.equipped_weapon["limit"] == 15:
                self.weapon_label.config(
                text=f"Arma: {self.equipped_weapon['value']}"
                )
            else:
                self.weapon_label.config(
                text=f"Arma: {self.equipped_weapon['value']} (límite <= {self.equipped_weapon['limit']})"
                )
        else:
            self.weapon_label.config(text="Arma: (ninguna)")

        # Estado del botón de saltar sala:
        # solo disponible si:
        # - el salto está disponible
        # - la sala está completa (4 cartas)
        if self.skip_available and len(self.room_cards) == 4:
            self.skip_button.config(state="normal", text="Saltar sala")
        else:
            self.skip_button.config(state="disabled", text="Saltar sala(no disponible)")

    def end_run(self, victory):
        for btn in self.card_buttons:
            btn.config(state="disabled")

        self.skip_button.config(state="disabled")

        if victory:
            msg = (
                "¡Victoria!\n"
                f"HP restante: {self.player_hp}\n"
                f"Puntuación: {self.score}\n"
                f"Seed: {self.current_seed}"
            )
        else:
            msg = (
                "Derrota...\n"
                f"Puntuación: {self.score}\n"
                f"Seed: {self.current_seed}"
            )

        messagebox.showinfo("Fin de la partida", msg)


# ==========================
# EJECUCIÓN
# ==========================

if __name__ == "__main__":
    root = tk.Tk()
    app = CartasMalditasApp(root)
    root.mainloop()
