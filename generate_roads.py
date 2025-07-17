import math
def generate_roads(houses, min_distance=2, delta_grid_size=30, shift_diagonally=False):
    """
    Генерирует дороги между домами, начиная от дверей и обходя препятствия.
    Возвращает список дорог, где каждая дорога - список точек [(x1,y1), (x2,y2), ...]

    Параметры
    -------
    houses : list
        список домов (x центр, y центр, x длина, y длина, положение двери, id_дома)
    min_distance : int
        минимальная дистанция между домом и дорогой
    delta_grid_size : int
        Дополнительное место для дорог.
    shift_diagonally : bool
        Диагональные дороги.
    """
    if len(houses) < 2:
        return []

    # Создаем карту домов и их входов
    house_map = {}
    door_positions = []
    
    grid_size=[[0,1], [0,1]]
    
    for i, house in enumerate(houses):
        x, y, w, h, door, _id = house
        # Определяем точку перед дверью (отступ min_distance)
        door_x = x - w//2 + door - 1
        door_y = y - h//2 - min_distance
        door_pos = (door_x, door_y)
        door_positions.append(door_pos)
        x1 = x - w//2 - min_distance
        y1 = y - h//2 - min_distance+1
        x2 = x + w//2 + min_distance
        y2 = y + h//2 + min_distance
        # Запоминаем границы дома с учетом min_distance
        house_map[i] = {
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'door': door_pos
        }
        if x1<=door_pos[0]<=x2 and y1<=door_pos[1]<=y2:
            print(door_pos, x1,y1,x2,y2)
        grid_size = [[min(grid_size[0][0], x1-delta_grid_size,x2-delta_grid_size), max(grid_size[0][1], x1+delta_grid_size,x2+delta_grid_size)],
                     [min(grid_size[1][0], y1-delta_grid_size,y2-delta_grid_size), max(grid_size[1][1], y1+delta_grid_size,y2+delta_grid_size)]]
    #print(grid_size)
    #Создаём сетку домов
    
    # Начинаем строить дорожную сеть с первого дома
    road_network = {door_positions[0]}
    roads = [[(door_positions[0][0], door_positions[0][1]+i) for i in range(1,min_distance+1)]]
    # Соединяем остальные дома
    for i in range(1, len(door_positions)):
        start_pos = door_positions[i]
        target_pos = find_nearest_road(start_pos, road_network)
        
        if target_pos:
            path = build_path(start_pos, target_pos, house_map, grid_size, shift_diagonally)
            if path:
                roads.append([(start_pos[0], start_pos[1]+i) for i in range(1,min_distance+1)]+path)
                # Добавляем все точки пути в дорожную сеть
                for point in path:
                    road_network.add(point)

    return roads
def find_nearest_road(point, road_network):
    """Находит ближайшую точку дорожной сети"""
    if not road_network:
        return None
    return min(road_network, key=lambda p: distance(p, point))
def distance(p1, p2):
    """Вычисляет расстояние между двумя точками"""
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
import heapq

def build_path(start, goal, forbidden_rects, grid_size, shift_diagonally=False):
    """Находит путь от start в goal, обходя forbidden_rects"""
    
    def in_bounds(p):
        x, y = p
        return grid_size[0][0] <= x < grid_size[0][1] and grid_size[1][0] <= y < grid_size[1][1]

    def heuristic(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def neighbors(p):
        x, y = p
        shifts = [(-1,0), (1,0), (0,-1), (0,1)]
        if shift_diagonally:
            shifts+=[(-1,-1), (-1,1), (1,-1), (1,1)]
        for dx, dy in shifts:
            np = (x+dx, y+dy)
            if in_bounds(np) and np not in blocked:
                yield np

    # Собираем все запрещённые клетки
    blocked = set()
    for rec in forbidden_rects:
        x1, y1, x2, y2 = forbidden_rects[rec]['x1'],forbidden_rects[rec]['y1'],forbidden_rects[rec]['x2'],forbidden_rects[rec]['y2']
        for x in range(int(x1), int(x2+1)):
            for y in range(int(y1), int(y2+1)):
                blocked.add((x, y))

    frontier = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for next_p in neighbors(current):
            new_cost = cost_so_far[current] + 1
            if next_p not in cost_so_far or new_cost < cost_so_far[next_p]:
                cost_so_far[next_p] = new_cost
                priority = new_cost + heuristic(goal, next_p)
                heapq.heappush(frontier, (priority, next_p))
                came_from[next_p] = current

    # Восстановить путь
    if goal not in came_from:
        return None

    path = []
    curr = goal
    while curr:
        path.append(curr)
        curr = came_from[curr]
    path.reverse()
    return path
