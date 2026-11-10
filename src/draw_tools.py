from tkinter import Canvas


def draw_rooms(canvas: Canvas,numbers_room: int,room_long: int, p_x :int,p_y: int):
    for i in range(numbers_room):
        for j in range(numbers_room):
            x1 = j * room_long
            y1 = i * room_long
            x2 = x1 + room_long
            y2 = y1 + room_long
            canvas.create_rectangle(x1, y1, x2, y2, outline="#E0E0E0")


def draw_marker(canvas: Canvas, x: int, y: int, room_long: int, tag: str, color: str, text: str):
    """Закрашивает комнату (x, y) цветом и подписывает (пожар / выход)."""
    pad = 4
    canvas.create_rectangle(x * room_long + pad, y * room_long + pad,
                            (x + 1) * room_long - pad, (y + 1) * room_long - pad,
                            fill=color, outline="", tags=tag)
    canvas.create_text(x * room_long + room_long // 2, y * room_long + 14,
                       text=text, font=("Arial", 11, "bold"), tags=tag)
