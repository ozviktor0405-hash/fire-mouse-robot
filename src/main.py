from tkinter import *
from robot_controll import draw_player
root = Tk()
root.title("цифровой макет")
radius = int(input("введите размеры робота "))
room_long = 200
nombers_room = int(input("количевство комнат " ))
long_all_rooms = room_long * nombers_room

canvas = Canvas(root, width=long_all_rooms, height=long_all_rooms, bg="white")
canvas.pack(padx=20, pady=20)

# Рисуем сетку комнат
from draw_tools import draw_rooms
# === ДОБАВИЛИ: 1. Виртуальные координаты положения робота в комнатах ===
p_x = int(input("введите начальную координату по x "))
p_y = int(input("введите начальную координату по y "))


# === ДОБАВИЛИ: 2. Функция, которая стирает старый и рисует нового робота ===
from robot_controll import draw_player

from robot_controll import wall_conroll
v_walls = []
h_walls = []

# Создаем отрезки стен между комнатами
from robot_controll import walls
walls(nombers_room,room_long,Button,root,canvas,v_walls,h_walls)


# === ДОБАВИЛИ: 4. Главная функция движения робота по текстовым командам ===
from robot_controll import move_robot_to
p_x, p_y = move_robot_to("right", p_x, p_y, nombers_room, room_long, radius, canvas, v_walls, h_walls)


# Создаем маленькую функцию для выполнения шага
def make_step(direction):
    global p_x, p_y  # Разрешаем менять глобальные координаты в main.py
    # Вот он — вызов нашей функции из другого файла!
    p_x, p_y = move_robot_to(direction, p_x, p_y, nombers_room, room_long, radius, canvas, v_walls, h_walls)

draw_player(room_long, radius, canvas, p_x, p_y)

# === ДОБАВИЛИ: 5. Цепочка автоматических команд по таймеру (робот ходит сам) ===
root.after(1000, lambda: make_step("right"))  # Через 1 секунду идет Вправо)
root.mainloop()
