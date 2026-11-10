from tkinter import Button, Canvas, Tk
def draw_player(room_long: int,radius: int,canvas: Canvas,p_x: int,p_y: int):
    canvas.delete("player")  # Находим старый кружок по тегу и стираем его
    cx = p_x * room_long + room_long // 2  # Находим пиксельный центр комнаты X
    cy = p_y * room_long + room_long // 2  # Находим пиксельный центр комнаты Y
    # Рисуем зеленую точку и вешаем на неё ярлык tags="player"
    canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#4CAF50", outline="black", tags="player")


# Файл: robot_logic.py

# Импортируем отрисовку, так как она вызывается в самом конце шага
from robot_control import draw_player


def move_robot_to(direction: str, p_x: int, p_y: int, numbers_room: int, room_long: int, radius: int, canvas: Canvas, v_walls: list, h_walls: list) -> tuple:
    # === Рождение old_x и old_y (создание слепка-страховки) ===
    old_x, old_y = p_x, p_y

    # Виртуальный шаг робота в памяти
    if direction == "up":
        p_y -= 1
    elif direction == "down":
        p_y += 1
    elif direction == "left":
        p_x -= 1
    elif direction == "right":
        p_x += 1
    else:
        return p_x, p_y  # Если команда не распознана, возвращаем координаты без изменений

    # === Проверка внешних границ макета ===
    if p_x < 0 or p_x > (numbers_room - 1) or p_y < 0 or p_y > (numbers_room - 1):
        p_x, p_y = old_x, old_y  # Если вылетел — восстанавливаем из страховки
        return p_x, p_y  # Возвращаем старые координаты

    # === Проверка твёрдости построенных стен ===
    wall_to_check = None

    if p_x != old_x:  # Шаг влево или вправо (пересекаем вертикальную стену)
        wall_index = old_y * (numbers_room - 1) + min(old_x, p_x)  # Динамическая формула для любого размера поля
        wall_to_check = v_walls[wall_index]

    elif p_y != old_y:  # Шаг вверх или вниз (пересекаем горизонтальную стену)
        wall_index = min(old_y, p_y) * numbers_room + old_x  # Динамическая формула для любого размера поля
        wall_to_check = h_walls[wall_index]

    # ФИЗИКА ТВЕРДОСТИ: если стена на пути ЧЁРНАЯ — отменяем шаг
    if wall_to_check and wall_to_check["bg"] == "black":
        p_x, p_y = old_x, old_y  # Возвращаем робота назад
        return p_x, p_y  # Возвращаем старые координаты

    # Если преград нет — успешно рисуем робота на новом месте!
    draw_player(room_long, radius, canvas, p_x, p_y)

    # ОБЯЗАТЕЛЬНО: отдаем новые измененные координаты обратно в main.py
    return p_x, p_y

def walls_to_bool(buttons: list) -> list:
    """Кнопки стен tkinter -> список bool (True = стена) для route_tools / Pico."""
    return [b["bg"] == "black" for b in buttons]


def wall_control(button: Button):
    if button["bg"] == "#CCCCCC":
        button.config(bg="black")
    else:
        button.config(bg="#CCCCCC")
def walls(numbers_room: int,room_long: int,Button: type[Button],root: Tk,canvas: Canvas,v_walls: list,h_walls: list):
    for i in range(numbers_room):
        for j in range(numbers_room):
            x_right = (j + 1) * room_long
            y_top = i * room_long
            x_left = j * room_long
            y_bottom = (i + 1) * room_long

            # Вертикальные стены
            if j < numbers_room - 1:
                v_wall = Button(root, bg="#CCCCCC", activebackground="black", bd=0)
                canvas.create_window(x_right, y_top + room_long // 2, window=v_wall, width=6, height=room_long)
                v_wall.config(command=lambda w=v_wall: wall_control(w))
                # === ДОБАВИЛИ: Кладем вертикальную кнопку в коробку v_walls ===
                v_walls.append(v_wall)

            # Горизонтальные стены
            if i < numbers_room - 1:
                h_wall = Button(root, bg="#CCCCCC", activebackground="black", bd=0)
                canvas.create_window(x_left + room_long // 2, y_bottom, window=h_wall, width=room_long, height=6)
                h_wall.config(command=lambda w=h_wall: wall_control(w))
                # === ДОБАВИЛИ: Кладем горизонтальную кнопку в коробку h_walls ===
                h_walls.append(h_wall)
