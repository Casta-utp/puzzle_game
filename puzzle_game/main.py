# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
import random
from solver import a_star, is_solvable
from kivy.uix.button import Button

class MainScreen(Screen):
    pass

class GameScreen(Screen):
    pass

class PuzzleGame(BoxLayout):
    size_n = NumericProperty(3)
    state = ListProperty([])
    moves = NumericProperty(0)
    solution_path = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Esperar a que el widget y sus ids estén listos
        Clock.schedule_once(self._finish_init)

        # atributo para guardar el evento de Clock (si hay resolución automática en curso)
        self._auto_event = None

    def _finish_init(self, *args):
        # inicializar tablero al terminar la construcción
        if not self.state:
            self.reset_board()

    def reset_board(self):
        """Genera un tablero resoluble y reinicia contador."""
        self.moves = 0
        self.solution_path = []
        self.state = list(range(1, self.size_n ** 2)) + [0]
        # lograr un estado aleatorio resoluble
        while True:
            random.shuffle(self.state)
            if is_solvable(self.state, self.size_n):
                break
        self.update_board()

    def update_board(self):
        """Dibuja botones en el grid y actualiza contador en la UI."""
        grid = self.ids.grid
        grid.clear_widgets()
        grid.cols = self.size_n
        grid.rows = self.size_n
        for value in self.state:
            if value == 0:
                btn = Button(text="", disabled=True, background_color=(0.5, 0.5, 0.5, 1))
            else:
                btn = Button(text=str(value), font_size=32)
                # fijar valor por defecto en lambda para evitar captura de variable
                btn.bind(on_release=lambda b, v=value: self.on_tile_pressed(v))
            grid.add_widget(btn)

        # actualizar el label de movimientos en la pantalla de juego
        try:
            app = App.get_running_app()
            app.sm.get_screen("game").ids.moves_label.text = f"Movimientos: {self.moves}"
        except Exception:
            # si por alguna razón no está disponible, ignorar
            pass

    def on_tile_pressed(self, value):
        """Llamado cuando se pulsa una ficha (UI)."""
        moved = self.move_tile(value)
        if moved:
            self.moves += 1
            self.update_board()

    def move_tile(self, value):
        """Mueve ficha si es válido; devuelve True si realizó un movimiento."""
        try:
            idx = self.state.index(value)
        except ValueError:
            return False
        zero_idx = self.state.index(0)
        size = self.size_n
        # vecino vertical u horizontal
        if abs(idx - zero_idx) == size or (abs(idx - zero_idx) == 1 and idx // size == zero_idx // size):
            self.state[zero_idx], self.state[idx] = self.state[idx], self.state[zero_idx]
            return True
        return False

    def start_manual(self):
        # cancelar cualquier autómata en curso
        self.cancel_auto()
        self.reset_board()

    def start_auto(self):
        # cancelar posible evento anterior
        self.cancel_auto()
        goal = tuple(list(range(1, self.size_n ** 2)) + [0])
        # a_star espera tupla/lista; devuelve lista de moves (strings) o None
        path = a_star(tuple(self.state), goal)
        if not path:
            # No debería ocurrir si el estado es resoluble, pero por seguridad:
            print("No se encontró solución (o tomó demasiado).")
            return
        self.solution_path = path[:]
        # agendar la reproducción de la solución (se almacena el evento)
        self._auto_event = Clock.schedule_interval(self._auto_step, 0.5)

    def _auto_step(self, dt):
        if not self.solution_path:
            self._auto_event = None
            return False  # devuelve False para desagendar
        move = self.solution_path.pop(0)
        self.auto_move(move)
        self.moves += 1
        self.update_board()
        return True

    def auto_move(self, move):
        size = self.size_n
        zero_idx = self.state.index(0)
        x, y = zero_idx % size, zero_idx // size
        moves = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        dx, dy = moves[move]
        new_x, new_y = x + dx, y + dy
        new_idx = new_y * size + new_x
        self.state[zero_idx], self.state[new_idx] = self.state[new_idx], self.state[zero_idx]

    def cancel_auto(self):
        if getattr(self, "_auto_event", None):
            try:
                self._auto_event.cancel()
            except Exception:
                # si no se puede cancelar directamente, intentar unschedule por callable
                Clock.unschedule(self._auto_step)
            self._auto_event = None
            self.solution_path = []

class PuzzleApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(GameScreen(name="game"))
        # referencia al juego actual (PuzzleGame que insertamos en game_box)
        self.current_game = None
        return self.sm

    def start_game(self, size):
        # crear widget de juego e insertarlo en game_box
        game_widget = PuzzleGame()
        game_widget.size_n = size
        # reset_board se llamará en _finish_init, pero llamar explícitamente asegura estado correcto
        game_widget.reset_board()
        self.current_game = game_widget
        game_box = self.sm.get_screen("game").ids.game_box
        game_box.clear_widgets()
        game_box.add_widget(game_widget)
        self.sm.current = "game"

    def reset_game(self):
        if self.current_game:
            self.current_game.reset_board()

    def go_back(self):
        # si hay resolución automática en curso, cancelarla
        if self.current_game:
            self.current_game.cancel_auto()
        self.sm.current = "main"

if __name__ == '__main__':
    PuzzleApp().run()
