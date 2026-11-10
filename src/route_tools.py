# Модуль работает и на ПК (CPython), и на Raspberry Pi Pico W (MicroPython):
# без tkinter, без collections.deque (в MicroPython у него другая сигнатура),
# без зависимостей от кнопок интерфейса. Карта -- обычные списки bool.
#
# Карта (numbers_room x numbers_room комнат):
#   v_walls[y * (n - 1) + x] -- True, если есть стена между комнатами (x, y) и (x + 1, y)
#   h_walls[y * n + x]       -- True, если есть стена между комнатами (x, y) и (x, y + 1)
# Y растёт вниз, старт робота -- правый нижний угол, смотрит вверх.

MOVES = (("up", 0, -1), ("down", 0, 1), ("left", -1, 0), ("right", 1, 0))


def map_to_dict(n, v_walls, h_walls, fire, exit_room, start):
    """Карта -> словарь, который сериализуется в JSON и уходит с ПК на Pico."""
    return {
        "n": n,
        "v": [1 if w else 0 for w in v_walls],
        "h": [1 if w else 0 for w in h_walls],
        "fire": [list(r) for r in fire],
        "exit": list(exit_room),
        "start": list(start),
    }


def map_from_dict(d):
    """Обратно (на Pico после json.loads): n, v_walls, h_walls, fire, exit, start."""
    return (
        d["n"],
        [bool(w) for w in d["v"]],
        [bool(w) for w in d["h"]],
        set(tuple(r) for r in d["fire"]),
        tuple(d["exit"]),
        tuple(d["start"]),
    )


def _is_wall(x, y, nx, ny, n, v_walls, h_walls):
    if nx != x:
        return v_walls[y * (n - 1) + min(x, nx)]
    return h_walls[min(y, ny) * n + x]


def _bfs(start, n, v_walls, h_walls, fire):
    """Поиск в ширину из start. Возвращает came_from:
    комната -> (предыдущая комната, команда) или None для start.
    В комнаты из fire въезжать нельзя."""
    came_from = {start: None}
    queue = [start]  # список + индекс вместо deque: popleft за O(1)
    head = 0
    while head < len(queue):
        x, y = queue[head]
        head += 1
        for command, dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < n and 0 <= ny < n):
                continue
            if (nx, ny) in came_from or (nx, ny) in fire:
                continue
            if _is_wall(x, y, nx, ny, n, v_walls, h_walls):
                continue
            came_from[(nx, ny)] = ((x, y), command)
            queue.append((nx, ny))
    return came_from


def _restore(came_from, goal):
    route = []
    room = goal
    while came_from[room] is not None:
        room, command = came_from[room]
        route.append(command)
    route.reverse()
    return route


def find_route(start, goal, n, v_walls, h_walls, fire=()):
    """Кратчайший маршрут start -> goal (BFS).

    fire -- комнаты-пожар (кортежи (x, y)), в них ехать нельзя.
    Возвращает список команд ["up", "left", ...], [] если start == goal,
    None если пути нет.
    """
    if start in fire or goal in fire:
        return None
    came_from = _bfs(start, n, v_walls, h_walls, fire)
    if goal not in came_from:
        return None
    return _restore(came_from, goal)


def find_escape_route(start, exit_room, n, v_walls, h_walls, fire):
    """Маршрут к выходу; если выход недостижим (пожар перекрыл), -- маршрут
    в достижимую комнату, самую дальнюю от пожара (по числу шагов, BFS
    от всех комнат пожара, стены учитываются, пожар проходим для замера)."""
    route = find_route(start, exit_room, n, v_walls, h_walls, fire)
    if route is not None:
        return route

    reachable = _bfs(start, n, v_walls, h_walls, fire)

    # расстояния от пожара: многоисточниковый BFS
    dist = {}
    queue = []
    for room in fire:
        dist[room] = 0
        queue.append(room)
    head = 0
    while head < len(queue):
        x, y = queue[head]
        head += 1
        for _, dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < n and 0 <= ny < n) or (nx, ny) in dist:
                continue
            if _is_wall(x, y, nx, ny, n, v_walls, h_walls):
                continue
            dist[(nx, ny)] = dist[(x, y)] + 1
            queue.append((nx, ny))

    # комнаты, до которых от пожара не добраться, -- самые безопасные
    best, best_d = start, -1
    for room in reachable:
        d = dist.get(room, n * n + 1)
        if d > best_d:
            best, best_d = room, d
    return _restore(reachable, best)
