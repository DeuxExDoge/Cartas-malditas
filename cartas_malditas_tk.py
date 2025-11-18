import tkinter as tk
from tkinter import messagebox
import random

# ==========================
# CONFIGURACIÓN DEL JUEGO
# ==========================

MAX_HP = 20

# Cada carta es un diccionario:
# {
#   "suit": "♥" / "♦" / "♣" / "♠",
#   "type": "potion" / "weapon" / "monster",
#   "value": int (2..9)
# }


class CartasMalditasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cartas Malditas - MVP Tkinter")

        # ---------- ESTADO DEL JUEGO ----------
        self.deck = []              # mazo
        self.room_cards = []        # cartas de la sala actual (máx. 4)
        self.carry_card = None      # carta arrastrada a la siguiente sala
        self.player_hp = MAX_HP
        self.equipped_weapon = None
        self.score = 0

        # ---------- UI SUPERIOR ----------
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)

        self.hp_label = tk.Label(top_frame, text="HP: 20", width=15)
        self.hp_label.grid(row=0, column=0, padx=5)

        self.weapon_label = tk.Label(top_frame, text="Arma: (ninguna)", width=20)
        self.weapon_label.grid(row=0, column=1, padx=5)

        self.deck_label = tk.Label(top_frame, text="Mazo: 0", width=15)
        self.deck_label.grid(row=0, column=2, padx=5)

        self.score_label = tk.Label(top_frame, text="Puntuación: 0", width=20)
        self.score_label.grid(row=0, column=3, padx=5)

        # ---------- UI CARTAS DE LA SALA ----------
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

        # ---------- UI CARTA ARRASTRADA ----------
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(pady=10)

        tk.Label(bottom_frame, text="Carta arrastrada:").grid(row=0, column=0, padx=5)

        self.carry_button = tk.Button(
            bottom_frame,
            text="Vacío",
            width=18,
            height=3,
            state="disabled"  # solo muestra info, no se juega
        )
        self.carry_button.grid(row=0, column=1, padx=5)

        # ---------- BOTÓN REINICIAR ----------
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)

        self.restart_button = tk.Button(
            control_frame,
            text="Reiniciar partida",
            command=self.start_new_run
        )
        self.restart_button.pack()

        # Empezar primera partida
        self.start_new_run()

    # ==========================
    # INICIALIZACIÓN DE PARTIDA
    # ==========================

    def start_new_run(self):
        """Reinicia todo el estado del juego."""
        self.player_hp = MAX_HP
        self.equipped_weapon = None
        self.score = 0
        self.carry_card = None

        self.build_deck()
        random.shuffle(self.deck)

        # Habilitar los botones de cartas por si estaban deshabilitados
        for btn in self.card_buttons:
            btn.config(state="normal")

        self.next_room()
        self.update_ui()

    def build_deck(self):
        """Construye un mazo con:
        - ♥ y ♦: 2–10
        - ♣ y ♠: 2–A (2–14, con J/Q/K/A como 11–14)
        """
        self.deck = []

        # 2–10 para TODOS los palos
        for value in range(2, 11):  # 2..10
            # ♥ pociones
            self.deck.append({"suit": "♥", "type": "potion", "value": value})
            # ♦ armas
            self.deck.append({"suit": "♦", "type": "weapon", "value": value})
            # ♣ monstruos
            self.deck.append({"suit": "♣", "type": "monster", "value": value})
            # ♠ monstruos
            self.deck.append({"suit": "♠", "type": "monster", "value": value})

        # Figuras J(11), Q(12), K(13), A(14) SOLO en palos negros (♣ y ♠)
        for value in range(11, 15):  # 11..14
            self.deck.append({"suit": "♣", "type": "monster", "value": value})
            self.deck.append({"suit": "♠", "type": "monster", "value": value})


    # ==========================
    # MANEJO DE SALAS
    # ==========================

    def next_room(self):
        """Genera la siguiente sala de hasta 4 cartas."""
        self.room_cards = []

        # La carta arrastrada entra a la nueva sala
        if self.carry_card is not None:
            self.room_cards.append(self.carry_card)
            self.carry_card = None

        # Rellenar con cartas del mazo hasta tener 4 o quedarse sin mazo
        while len(self.room_cards) < 4 and self.deck:
            self.room_cards.append(self.deck.pop())

        # Si ya no quedan cartas ni en sala ni en mazo → fin de partida
        if not self.room_cards and not self.deck and self.carry_card is None:
            self.end_run(victory=self.player_hp > 0)
            return

        self.update_cards_ui()

    def update_cards_ui(self):
        """Actualiza texto/estado de los botones de cartas y el slot arrastrado."""
        for i, btn in enumerate(self.card_buttons):
            if i < len(self.room_cards):
                card = self.room_cards[i]
                btn.config(
                    text=self.get_card_label(card),
                    state="normal"
                )
            else:
                btn.config(text="", state="disabled")

        if self.carry_card is not None:
            self.carry_button.config(
                text=self.get_card_label(self.carry_card)
            )
        else:
            self.carry_button.config(text="Vacío")

        self.update_ui()

    def get_card_label(self, card):
        """Devuelve el texto descriptivo de una carta para mostrar en el botón."""
        type_name = {
            "potion": "Poción",
            "weapon": "Arma",
            "monster": "Monstruo"
        }.get(card["type"], "?")

        v = card["value"]
        if v == 11:
            rank = "J"
        elif v == 12:
            rank = "Q"
        elif v == 13:
            rank = "K"
        elif v == 14:
            rank = "A"
        else:
            rank = str(v)

        return f"{card['suit']} {rank} ({type_name})"



    # ==========================
    # LÓGICA AL JUGAR CARTAS
    # ==========================

    def on_card_button_pressed(self, index):
        """Se llama cuando el jugador hace click en una carta de la sala."""
        if index >= len(self.room_cards):
            return

        card = self.room_cards[index]

        if card["type"] == "monster":
            self.play_monster(card)
        elif card["type"] == "potion":
            self.play_potion(card)
        elif card["type"] == "weapon":
            self.play_weapon(card)

        # Eliminamos la carta jugada de la sala
        del self.room_cards[index]

        # ¿murió el jugador?
        if self.player_hp <= 0:
            self.end_run(victory=False)
            return

        # Si queda solo 1 carta en sala → se arrastra y se genera nueva sala
        if len(self.room_cards) == 1:
            self.carry_card = self.room_cards[0]
            self.room_cards = []
            self.next_room()
        else:
            # Seguimos en la misma sala
            self.update_cards_ui()

    def play_monster(self, card):
        """Resuelve el combate contra un monstruo considerando el sistema de límite."""

        monster_value = card["value"]

        # Si NO hay arma equipada → daño completo
        if self.equipped_weapon is None:
            self.player_hp -= monster_value
            self.score += 1
            return

        weapon_limit = self.equipped_weapon["limit"]

        # ¿El arma puede bloquear este monstruo?
        if monster_value <= weapon_limit:
            # Muerte exitosa sin recibir daño
            self.score += 1

            # Reducir límite del arma al valor del monstruo derrotado
            self.equipped_weapon["limit"] = monster_value

            # Si querés ver el límite actual en consola:
            # print("Nuevo límite del arma:", self.equipped_weapon["limit"])

        else:
            # No puede matar → recibimos daño completo
            self.player_hp -= monster_value
            self.score += 1
            # El arma NO se pierde y NO cambia su límite


    def play_potion(self, card):
        """Aplica el efecto de una poción."""
        self.player_hp += card["value"]
        if self.player_hp > MAX_HP:
            self.player_hp = MAX_HP

    def play_weapon(self, card):
        """Equipa un arma y asigna su límite inicial igual a su valor."""
        self.equipped_weapon = {
            "suit": card["suit"],
            "type": "weapon",
            "value": card["value"],
            "limit": card["value"]  # nuevo: límite inicial = daño del arma
        }


    # ==========================
    # UI GENERAL Y FIN DE RUN
    # ==========================

    def update_ui(self):
        """Actualiza los labels de HP, arma, mazo y puntuación."""
        self.hp_label.config(text=f"HP: {self.player_hp}")
        self.deck_label.config(text=f"Mazo: {len(self.deck)}")
        self.score_label.config(text=f"Puntuación: {self.score}")

        if self.equipped_weapon is not None:
            self.weapon_label.config(
                text=f"Arma: {self.equipped_weapon['value']} (limite {self.equipped_weapon['limit']})"
            )

        else:
            self.weapon_label.config(text="Arma: (ninguna)")

    def end_run(self, victory):
        """Muestra mensaje de victoria/derrota y deshabilita las cartas."""
        for btn in self.card_buttons:
            btn.config(state="disabled")

        if victory:
            msg = f"¡Victoria!\nHP restante: {self.player_hp}\nPuntuación: {self.score}"
        else:
            msg = f"Derrota...\nPuntuación: {self.score}"

        messagebox.showinfo("Fin de la partida", msg)


# ==========================
# PUNTO DE ENTRADA
# ==========================

if __name__ == "__main__":
    root = tk.Tk()
    app = CartasMalditasApp(root)
    root.mainloop()
