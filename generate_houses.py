import random
import math
import hashlib

def random_generate_houses_list(count_house,sizeX=[2,5], sizeY=[2,5], seed=None):
    if not seed:
        rnd = random.Random()
    elif seed and (not (type(seed) == int and 0<=seed<2**64)):
        seed = stable_to_uint64(seed)
        rnd = random.Random(seed)
    else:
        rnd = random.Random(seed)
    id_counter = rnd.randint(0,10000)
    list_rand_h = [0.]+sorted([rnd.random() for i in range(count_house-1)])+[1.]
    house_list = [[[xh:=rnd.randrange(sizeX[0],sizeX[1]), rnd.randrange(sizeY[0],sizeY[1])], rnd.randrange(1,xh),id_counter+i, list_rand_h[i+1]-list_rand_h[i]] for i in range(count_house)]
    return house_list
def stable_to_uint64(value) -> int:
    data = str(value).encode('utf-8')
    digest = hashlib.sha256(data).digest()
    return int.from_bytes(digest[:8], 'big')
class Generator_houses():
    def __init__(self, min_dist, attach_dist_min, attach_dist_max, max_village_radius=None, seed=None):
        """Класс генератора домов деревни

        Параметры
        -------
        min_dist : int
            Минимально растояние между чужими домами
        attach_dist_min : int
            минимальное растояние между родительским домом и дочерним
        attach_dist_max : int
            максимальное растояние между родительским домом и дочерним
        max_village_radius : int/None
            максимальный радиус деревни, None - если нет ограничений (None по умолчанию)
        seed : int | float | str | bytes | bytearray
            сид для генерации, None - случайное (None по умолчанию)
        """
        self.min_dist = min_dist
        self.attach_dist_min = attach_dist_min
        self.attach_dist_max = attach_dist_max
        self.max_village_radius = max_village_radius
        self.houses = []
        self.attachable_houses = set()
        self.max_iterations = 100
        if not seed:
            seed = random.randint(0, 2**64-1)
        elif not (type(seed) == int and 0<=seed<2**64):
            seed = stable_to_uint64(seed)
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_houses(self,house_templates, count_house):
        """Генерирует деревню из `num_houses` домов без дорог.
        
        Параметры
        ------
        house_templates  : list
            Список шаблонов домов.
        count_house : int
            желательное и максимальное количество сгенерированных домов"""
        if count_house < 1:
            return []
        
        # Разделяем дома на случайные и специальные
        p_h = 0
        house_random = []
        for i in house_templates:
            if type(i[-1]) == float and 0 < i[-1] <= 1:
                house_random.append(i[:-1] + [p_h, p_h + i[-1]] + [i[-1]])
                p_h += i[-1]
        
        # Проверка суммы вероятностей
        sum_err = sum([i[-1] for i in house_random])
        if house_random and sum_err > 1 + 1e-5:
            raise ValueError(f'Сумма вероятностей домов должна быть равна 1 (или меньше): {sum_err}!=~1')
        
        # Обработка специальных домов
        house_special = [i for i in house_templates if type(i[-1]) == int and i[-1] >= 1]
        house_special.sort(key=lambda a: a[-2])
        house_gen_order = [0] * count_house
        
        for house_i in house_special:
            for i in range(house_i[-1]):
                if 0 in house_gen_order:
                    n_ = int(round(house_i[-2] * (count_house - 1)))
                    if house_gen_order[n_] == 0:
                        house_gen_order[n_] = (house_i[0][0], house_i[0][1], house_i[1], house_i[2], 1)
                    else:
                        delta_r = 1
                        while n_ + delta_r < count_house:
                            if house_gen_order[n_ + delta_r]:
                                break
                            delta_r += 1
                        delta_l = -1
                        while n_ + delta_l < count_house:
                            if house_gen_order[n_ + delta_l]:
                                break
                            delta_l -= 1
                        best_n = min(delta_r, delta_l, key=lambda a: abs(a))
                        if 0 <= n_ + best_n < count_house:
                            house_gen_order[best_n] = (house_i[0][0], house_i[0][1], house_i[1], house_i[2],1)
        
        # Заполняем оставшиеся дома случайными
        for i in range(count_house):
            if house_gen_order[i] == 0:
                r = self.rng.random()
                for h in house_random:
                    if h[-3] <= r < h[-2]:
                        house_gen_order[i] = (h[0][0], h[0][1], h[1], h[2], 0)
        #house_gen_order[0] = (x_len, y_len, door_block, id)

        # Начинаем с одного дома в центре
        if not self.houses:
            self.houses.append((0, 0, house_gen_order[0][0], house_gen_order[0][1])+house_gen_order[0][2:4])  # Добавляем первый дом
        
        # Множество домов, к которым можно пристраивать новые
        if not self.attachable_houses:
            self.attachable_houses.add(self.houses[-1][:4])

        for i_ in range(count_house - 1):
            self.add_house(house_gen_order[i_+1][:-1])
        
        return self.gethouses()
    def getseed(self):
        return self.seed
    def gethouses(self):
        """Возращает список сгенерированных домов с положением каждого дома в углу дома с меньшими кординатами"""
        return [(h[0]-h[2]//2, h[1]-h[3]//2)+h[2:] for h in self.houses]
    def add_house(self, info_new_houses):
        """Добавляет новый дом с учетом размеров существующих домов."""
        #info_new_houses = (x_len, y_len, door_block, id)
        #Проверям что дом есть к кому добавлять
        if len(self.attachable_houses) ==0:
            return None
        new_house_radius = self._calculate_house_radius((0,0)+info_new_houses)
        # Пытаемся прицепить новый дом к нескольким родительским домам
        for __ in range(3):
            parent_house = self.rng.choice(list(self.attachable_houses))
            parent_radius = self._calculate_house_radius(parent_house)
            
            for angle in self.generate_angles(self.max_iterations, 0.2):

                distance = self.rng.uniform(self.attach_dist_min, self.attach_dist_max)
                
                #Учитываем радиус родительского дома
                dx = int(round((distance + parent_radius+new_house_radius) * math.cos(angle)))
                dy = int(round((distance + parent_radius+new_house_radius) * math.sin(angle)))
                new_house = (parent_house[0] + dx, parent_house[1] + dy)+info_new_houses

                #Проверяем расстояние до всех домов с учетом их радиусов
                valid = True
                for h in self.houses:
                    if h == parent_house:
                        continue
                        
                    h_radius = self._calculate_house_radius(h)
                    dist = math.hypot(new_house[0] - h[0], new_house[1] - h[1])
                    
                    if dist < self.min_dist + new_house_radius + h_radius:
                        valid = False
                        break
                if self.max_village_radius is not None:
                    dist_from_center = math.hypot(new_house[0], new_house[1])
                    if dist_from_center > self.max_village_radius:
                        continue  # Пропускаем позиции за пределами радиуса
                    if valid:
                        break
                elif valid:
                    break
            if not valid:
                # Если не получилось, помечаем родительский дом как неприкрепляемый
                self.attachable_houses.discard(parent_house)
                new_house=self._expand_village(info_new_houses)
                continue
            break
        if not new_house == None:
            self.houses.append(new_house)
            self._update_attachable_houses(new_house)

    def _update_attachable_houses(self, new_house):
        """Обновляет множество attachable_houses с учетом размеров домов."""
        self.attachable_houses.add(new_house)
        for house in list(self.attachable_houses):
            house_radius = self._calculate_house_radius(house)
            if not self._has_space_around(house, house_radius):
                self.attachable_houses.discard(house)

    def _has_space_around(self, house, house_radius=None):
        """Проверяет, есть ли место вокруг дома для прикрепления нового."""
        if house_radius is None:
            house_radius = self._calculate_house_radius(house)
        for angle in self.generate_angles(self.max_iterations, 0.5):

            distance = self.rng.uniform(self.attach_dist_min, self.attach_dist_max)
            
            # Учитываем радиус текущего дома
            dx = int(round((distance + house_radius*2) * math.cos(angle)))
            dy = int(round((distance + house_radius*2) * math.sin(angle)))
            test_house = (house[0] + dx, house[1] + dy, house[2], house[3])
            test_radius = self._calculate_house_radius(test_house)

            valid = True
            for h in self.houses:
                if h == house:
                    continue
                    
                h_radius = self._calculate_house_radius(h)
                dist = math.hypot(test_house[0] - h[0], test_house[1] - h[1])
                
                if dist < self.min_dist + test_radius + h_radius:
                    valid = False
                    break
            
            if valid:
                return True
        
        return False

    def _expand_village(self, info_new_houses):
        """Добавляет дом на краю деревни, если это позволяет максимальный радиус"""
        if not self.houses:
            #Типо случайный дом
            return (0, 0, 4, 4,2,1)

        farthest_house = max(self.houses, key=lambda h: math.hypot(h[0], h[1]))
        farthest_radius = self._calculate_house_radius(farthest_house)
        new_house_radius = self._calculate_house_radius((0,0)+info_new_houses)
        if self.max_village_radius is not None:
            current_radius = math.hypot(farthest_house[0], farthest_house[1])
            if new_house_radius+ current_radius + self.attach_dist_max + farthest_radius > self.max_village_radius:
                # Ищем другое направление внутри допустимого радиуса
                for angle in self.generate_angles(self.max_iterations//2,0.5):  # Пробуем несколько направлений
                    distance = min(self.attach_dist_max, self.max_village_radius-current_radius - new_house_radius - farthest_radius)
                    if distance > self.min_dist:
                        new_x = farthest_house[0] + round(distance * math.cos(angle))
                        new_y = farthest_house[1] + round(distance * math.sin(angle))
                        return (new_x, new_y)+info_new_houses
                return None
        
        # Стандартная логика, если радиус не ограничен
        angle = math.atan2(farthest_house[1], farthest_house[0])+self.rng.uniform(-0.5*math.pi, 0.5*math.pi)
        distance = self.attach_dist_max + farthest_radius + new_house_radius
        new_x = farthest_house[0] + round(distance * math.cos(angle))
        new_y = farthest_house[1] + round(distance * math.sin(angle))
        return (new_x, new_y)+info_new_houses
    
    def generate_angles(self, count=20, segments = 1):
        """Генерирует необходимое количество случайных углов, гарантированно находящихся в n сегментах окружности"""
        if type(segments) == float:
            if 0<segments<1:
                segments = int(count*segments)
            else: segments = 1
        angle_in_one_segment = 2*math.pi/segments
        iter_segment = list(range(segments))
        self.rng.shuffle(iter_segment)
        for segment in iter_segment:
            count_angle = count//segments +1 if segment < count%segments else count//segments
            for _ in range(count_angle):
                angle = self.rng.uniform(segment*angle_in_one_segment, (segment+1)*angle_in_one_segment)
                yield angle

    @staticmethod
    def _calculate_house_radius(house):
        """Вычисляет радиус окружности, описывающей дом."""
        x_len, y_len = house[2], house[3]
        return math.sqrt((x_len/2)**2 + (y_len/2)**2)
    
    

        