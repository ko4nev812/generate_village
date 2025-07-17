import random
import math

def random_generate_houses_list(count_house,minsize=[2,5], maxsize=[2,5]):
    list_rand_h = [0.]+sorted([random.random() for i in range(count_house-1)])+[1.]
    house_list = [[[xh:=random.randrange(2,6), random.randrange(2,6)], random.randrange(1,xh),i, list_rand_h[i+1]-list_rand_h[i]] for i in range(count_house)]
    return house_list

def generate_houses(house_list, num_houses, min_dist, attach_dist_min, attach_dist_max, max_village_radius=None):
    """Генерирует деревню из `num_houses` домов без дорог.
    
    Параметры
    ------
    house_list : list
        Список домов.
    num_houses : int
        желательное и максимальное количество домов в деревне
    min_dist : int
        Минимально растояние между чужими домами
    attach_dist_min : int
        минимальное растояние между родительским домом и дочерним
    attach_dist_max : int
        максимальное растояние между родительским домом и дочерним
    max_village_radius : int/None
        максимальный радиус деревни, None - если нет ограничений"""
    if num_houses < 1:
        return []
    
    # Разделяем дома на случайные и специальные
    p_h = 0
    house_random = []
    for i in house_list:
        if type(i[-1]) == float and 0 < i[-1] <= 1:
            house_random.append(i[:-1] + [p_h, p_h + i[-1]] + [i[-1]])
            p_h += i[-1]
    
    # Проверка суммы вероятностей
    sum_err = sum([i[-1] for i in house_random])
    if sum_err > 1 + 1e-5:
        raise ValueError(f'Сумма вероятностей домов должна быть равна 1 (или меньше): {sum_err}!=~1')
    
    # Обработка специальных домов
    house_special = [i for i in house_list if type(i[-1]) == int and i[-1] >= 1]
    houses_priority = [0] * num_houses
    
    for house_i in house_special:
        for i in range(house_i[-1]):
            if 0 in houses_priority:
                n_ = int(round(house_i[-2] * (num_houses - 1)))
                if houses_priority[n_] == 0:
                    houses_priority[n_] = (house_i[0][0], house_i[0][1], house_i[1], house_i[2])
                else:
                    delta_r = 1
                    while n_ + delta_r < num_houses:
                        if houses_priority[n_ + delta_r]:
                            break
                        delta_r += 1
                    delta_l = -1
                    while n_ + delta_l < num_houses:
                        if houses_priority[n_ + delta_l]:
                            break
                        delta_l -= 1
                    best_n = min(delta_r, delta_l, key=lambda a: abs(a))
                    if 0 <= n_ + best_n < num_houses:
                        houses_priority[best_n] = (house_i[0][0], house_i[0][1], house_i[1], house_i[2])
    
    # Заполняем оставшиеся дома случайными
    for i in range(num_houses):
        if houses_priority[i] == 0:
            r = random.random()
            for h in house_random:
                if h[-3] <= r < h[-2]:
                    houses_priority[i] = (h[0][0], h[0][1], h[1], h[2])

    # Начинаем с одного дома в центре
    houses = [(0, 0, houses_priority[0][0], houses_priority[0][1], houses_priority[-1])]  # Добавляем размеры дома
    
    # Множество домов, к которым можно пристраивать новые
    attachable_houses = set([houses[0]])

    for i_ in range(num_houses - 1):
        new_house = add_house(
            houses, attachable_houses, (0,0)+houses_priority[i_+1], 
            min_dist, attach_dist_min, attach_dist_max,
            max_village_radius=max_village_radius
        )
        if not new_house == None:
            houses.append(new_house+tuple([houses_priority[i_+1][-1]]))
            update_attachable_houses(
                houses, attachable_houses, new_house, min_dist, attach_dist_min, attach_dist_max
            )
    
    # Собираем итоговый список домов с их типами
    houses_output = []
    for i, house in enumerate(houses):
        if i < len(houses_priority) and type(houses_priority[i]) != int:
            houses_output.append(house[:2] + houses_priority[i][:])
    
    return houses_output

def add_house(houses, attachable_houses, info_new_houses, min_dist, attach_dist_min, attach_dist_max, max_attempts=100, max_village_radius=None):
    """Добавляет новый дом с учетом размеров существующих домов."""
    #Проверям что дом есть к кому добавлять
    if len(attachable_houses) ==0:
        return None
    parent_house = random.choice(list(attachable_houses))
    parent_radius = calculate_house_radius(parent_house)
    new_house_radius = calculate_house_radius(info_new_houses)

    for _ in range(max_attempts):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(attach_dist_min, attach_dist_max)
        
        #Учитываем радиус родительского дома
        dx = int(round((distance + parent_radius+new_house_radius) * math.cos(angle)))
        dy = int(round((distance + parent_radius+new_house_radius) * math.sin(angle)))
        new_house = (parent_house[0] + dx, parent_house[1] + dy, parent_house[2], parent_house[3])

        #Проверяем расстояние до всех домов с учетом их радиусов
        valid = True
        for h in houses:
            if h == parent_house:
                continue
                
            h_radius = calculate_house_radius(h)
            dist = math.hypot(new_house[0] - h[0], new_house[1] - h[1])
            
            if dist < min_dist + new_house_radius + h_radius:
                valid = False
                break
        if max_village_radius is not None:
            dist_from_center = math.hypot(new_house[0], new_house[1])
            if dist_from_center > max_village_radius:
                continue  # Пропускаем позиции за пределами радиуса
            if valid:
                return new_house

    # Если не получилось, помечаем родительский дом как неприкрепляемый
    attachable_houses.discard(parent_house)
    return expand_village(houses, min_dist, attach_dist_max, max_village_radius)
def calculate_house_radius(house):
    """Вычисляет радиус окружности, описывающей дом."""
    x_len, y_len = house[2], house[3]
    return math.sqrt((x_len/2)**2 + (y_len/2)**2)

def update_attachable_houses(houses, attachable_houses, new_house, min_dist, attach_dist_min, attach_dist_max):
    """Обновляет множество attachable_houses с учетом размеров домов."""
    attachable_houses.add(new_house)

    for house in list(attachable_houses):
        house_radius = calculate_house_radius(house)
        if not has_space_around(house, houses, min_dist, attach_dist_min, attach_dist_max, house_radius):
            attachable_houses.discard(house)

def has_space_around(house, houses, min_dist, attach_dist_min, attach_dist_max, house_radius=None):
    """Проверяет, есть ли место вокруг дома для прикрепления нового."""
    if house_radius is None:
        house_radius = calculate_house_radius(house)

    for _ in range(30):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(attach_dist_min, attach_dist_max)
        
        # Учитываем радиус текущего дома
        dx = int(round((distance + house_radius*2) * math.cos(angle)))
        dy = int(round((distance + house_radius*2) * math.sin(angle)))
        test_house = (house[0] + dx, house[1] + dy, house[2], house[3])
        test_radius = calculate_house_radius(test_house)

        valid = True
        for h in houses:
            if h == house:
                continue
                
            h_radius = calculate_house_radius(h)
            dist = math.hypot(test_house[0] - h[0], test_house[1] - h[1])
            
            if dist < min_dist + test_radius + h_radius:
                valid = False
                break
        
        if valid:
            return True
    
    return False

def expand_village(houses, min_dist, attach_dist_max, max_village_radius=None):
    if not houses:
        return (0, 0, 20, 20)

    farthest_house = max(houses, key=lambda h: math.hypot(h[0], h[1]))
    farthest_radius = calculate_house_radius(farthest_house)
    
    if max_village_radius is not None:
        current_radius = math.hypot(farthest_house[0], farthest_house[1])
        if current_radius + attach_dist_max + farthest_radius > max_village_radius:
            # Ищем другое направление внутри допустимого радиуса
            for _ in range(20):  # Пробуем несколько случайных направлений
                angle = random.uniform(0, 2 * math.pi)
                distance = min(attach_dist_max, max_village_radius - current_radius - farthest_radius)
                if distance > min_dist:
                    new_x = farthest_house[0] + round(distance * math.cos(angle))
                    new_y = farthest_house[1] + round(distance * math.sin(angle))
                    return (new_x, new_y, farthest_house[2], farthest_house[3])
            return None
    
    # Стандартная логика, если радиус не ограничен
    angle = math.atan2(farthest_house[1], farthest_house[0])
    distance = attach_dist_max + farthest_radius
    new_x = farthest_house[0] + round(distance * math.cos(angle))
    new_y = farthest_house[1] + round(distance * math.sin(angle))
    return (new_x, new_y, farthest_house[2], farthest_house[3])