from generate_houses import generate_houses
from generate_roads import generate_roads
def generate_village(house_list, count_house, min_dist, attach_dist_minmax,min_distance=2,delta_grid_size=10,shift_diagonally=False, max_village_radius=None):
    """Генерация деревни с однонаправленным положением двери и дорог между домами.

    Параметры
    ----------
    house_list : list
        Список домов в специальном формате
    count_house : int
        Количество домов
    min_dist : int
        Минимальное растояние между чужими домами
    attach_dist_minmax : list
        минимально и максимальное растояние между родительским и дочерним домом, например [3,7] - случайное от 3 до 7
    min_distance : int
        Минимальное растояние от дома до мимо проходящей дороги
    delta_grid_size : int
        Дополнительное место для дорог (лучше не ставить меньше 10, иначе дороги могут не найти путь)
    shift_diagonally : bool
        Может ли дорога идти по диагонали
    max_village_radius : int
        Максимальный радиус деревни (None - без границ), если будет маленький, тогда может не хватить, чтобы поставить нужное количество домов
    """
    if not (attach_dist_minmax[0]<=min_dist<=attach_dist_minmax[1]):
        raise ValueError(f'Минимальное растояние между домами должно быть между attach_dist_minmax: {min_dist}>={attach_dist_minmax[0]} и {min_dist}<={attach_dist_minmax[1]}')
    houses = generate_houses(house_list, count_house, min_dist, attach_dist_minmax[0], attach_dist_minmax[1], max_village_radius=max_village_radius)
    print('Сгенерированно', len(houses), 'домов')

    roads = generate_roads(houses,min_distance,delta_grid_size,shift_diagonally)
    print('Сгенерированно', sum([len(i) for i in roads]), 'дорог')
    return houses, roads

if __name__=='__main__':
    #Пример

    #Создаём список из 20 случайных домов с шириной по х от 2 до 6 и длиной по у от 1 до 5
    from generate_houses import random_generate_houses_list
    house_list = random_generate_houses_list(20, [2,6], [1,5])

    #Генерируем деревню с мин растоянием между домами 7; растояние между сгенерированным домом и его предшественником от 7 до 10
    #Минимальным растоянием от дороги до дома 3; Максимальным радиусом деревни 100
    houses, roads = generate_village(house_list, 50, 7, [7,10],3, max_village_radius=100)
    
    #Создание .png картинки с соотношением 1:10 (1 блок = 10 пикселей на картинке)
    from vizualization_png import generate_village_image
    generate_village_image(houses, roads, cell_size=10)
    