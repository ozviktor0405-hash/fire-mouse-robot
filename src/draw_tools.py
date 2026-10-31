def draw_rooms(canvas, nombers_room: int,room_long: int, p_x :int,p_y: int):
    for i in range(nombers_room):
        for j in range(nombers_room):
            x1 = j * room_long
            y1 = i * room_long
            x2 = x1 + room_long
            y2 = y1 + room_long
            canvas.create_rectangle(x1, y1, x2, y2, outline="#E0E0E0")
