"""Цифровой макет (ПК). Только интерфейс: вся логика маршрута в route_tools.py,
которая без изменений работает на Raspberry Pi Pico W (MicroPython)."""
import json
from tkinter import Tk, Canvas, Frame, Button, Label, Spinbox, IntVar

from draw_tools import draw_rooms, draw_marker
from robot_control import draw_player, move_robot_to, walls, walls_to_bool
from route_tools import find_route, find_escape_route, map_to_dict

ROOM_LONG = 120   # пикселей на комнату
RADIUS = 30       # радиус робота на экране
MAX_ROOMS = 5
STEP_MS = 600     # пауза между шагами робота

HINT = ("Клик по ребру между комнатами -- поставить/убрать стену.\n"
        "Левый клик по комнате -- выход.  Правый клик по комнате -- пожар.\n"
        "Старт робота -- правый нижний угол.")


class App:
    def __init__(self, root: Tk):
        self.root = root
        root.title("цифровой макет")
        self.after_id = None
        self.running = False

        top = Frame(root)
        top.pack(pady=6)
        Label(top, text="Комнат по стороне:").pack(side="left")
        self.n_var = IntVar(value=3)
        Spinbox(top, from_=1, to=MAX_ROOMS, width=3, textvariable=self.n_var,
                state="readonly").pack(side="left")
        Button(top, text="Создать макет", command=self.build).pack(side="left", padx=6)
        self.run_btn = Button(top, text="Запустить", command=self.run)
        self.run_btn.pack(side="left", padx=6)
        Button(top, text="Сброс робота", command=self.reset_robot).pack(side="left")

        Label(root, text=HINT, justify="left").pack()
        self.status = Label(root, text="", fg="#555555")
        self.status.pack()
        self.board = Frame(root)
        self.board.pack(padx=20, pady=10)
        self.build()

    # ---------- построение макета ----------
    def build(self):
        self.stop()
        for w in self.board.winfo_children():
            w.destroy()
        self.n = self.n_var.get()
        size = ROOM_LONG * self.n
        self.canvas = Canvas(self.board, width=size, height=size, bg="white",
                             highlightthickness=0, bd=0)
        self.canvas.pack()
        draw_rooms(self.canvas, self.n, ROOM_LONG, 0, 0)
        self.v_walls, self.h_walls = [], []
        walls(self.n, ROOM_LONG, Button, self.board, self.canvas, self.v_walls, self.h_walls)
        self.canvas.bind("<Button-1>", self.on_left)
        self.canvas.bind("<Button-3>", self.on_right)
        self.fire = set()
        self.exit_room = None
        self.reset_robot()
        self.say("Макет создан. Расставьте стены, выход и пожар.")

    def say(self, text: str):
        self.status.config(text=text)

    def room_at(self, event):
        x, y = event.x // ROOM_LONG, event.y // ROOM_LONG
        if 0 <= x < self.n and 0 <= y < self.n:
            return (x, y)
        return None

    def redraw_markers(self):
        self.canvas.delete("fire", "exit")
        for fx, fy in self.fire:
            draw_marker(self.canvas, fx, fy, ROOM_LONG, "fire", "#FF8A80", "ПОЖАР")
        if self.exit_room:
            draw_marker(self.canvas, *self.exit_room, ROOM_LONG, "exit", "#A5D6A7", "ВЫХОД")
        self.canvas.tag_lower("fire")
        self.canvas.tag_lower("exit")
        self.canvas.tag_raise("player")

    # ---------- клики ----------
    def on_left(self, event):  # выход
        room = self.room_at(event)
        if self.running or room is None:
            return
        if room in self.fire:
            self.say("В горящей комнате выход ставить нельзя.")
            return
        self.exit_room = None if room == self.exit_room else room
        self.redraw_markers()

    def on_right(self, event):  # пожар
        room = self.room_at(event)
        if self.running or room is None:
            return
        if room == (self.px, self.py):
            self.say("Нельзя поджечь комнату, где стоит робот.")
            return
        if room == self.exit_room:
            self.say("Нельзя поджечь выход (сначала уберите выход левым кликом).")
            return
        self.fire.symmetric_difference_update({room})
        self.redraw_markers()

    # ---------- робот ----------
    def reset_robot(self):
        self.stop()
        self.px, self.py = self.n - 1, self.n - 1  # правый нижний угол
        draw_player(ROOM_LONG, RADIUS, self.canvas, self.px, self.py)
        self.redraw_markers()

    def stop(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.set_editing(True)

    def set_editing(self, enabled: bool):
        self.running = not enabled
        state = "normal" if enabled else "disabled"
        for b in getattr(self, "v_walls", []) + getattr(self, "h_walls", []):
            b.config(state=state)
        self.run_btn.config(state=state)

    def run(self):
        if self.running:
            return
        if self.exit_room is None:
            self.say("Сначала выберите выход (левый клик по комнате).")
            return
        v, h = walls_to_bool(self.v_walls), walls_to_bool(self.h_walls)
        start = (self.px, self.py)
        # то же самое (карта в JSON + find_escape_route) будет выполнять Pico
        print("карта для Pico:", json.dumps(
            map_to_dict(self.n, v, h, self.fire, self.exit_room, start)))
        reachable = find_route(start, self.exit_room, self.n, v, h, self.fire) is not None
        route = find_escape_route(start, self.exit_room, self.n, v, h, self.fire)
        self.say(f"Маршрут (BFS): {route}" if reachable else
                 f"Выход недоступен -- еду в самую дальнюю от пожара комнату: {route}")
        self.set_editing(False)
        self.steps = list(route)
        self.step()

    def step(self):
        if not self.steps:
            self.after_id = None
            self.set_editing(True)
            return
        command = self.steps.pop(0)
        self.px, self.py = move_robot_to(command, self.px, self.py, self.n, ROOM_LONG,
                                         RADIUS, self.canvas, self.v_walls, self.h_walls)
        self.after_id = self.root.after(STEP_MS, self.step)


if __name__ == "__main__":
    root = Tk()
    App(root)
    root.mainloop()
