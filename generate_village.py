from generate_houses import Generator_houses
from generate_roads import generate_roads


def generate_village(house_templates, count_house, min_dist, attach_dist_minmax,min_distance=2,delta_grid_size=10,shift_diagonally=False, max_village_radius=None, seed=None):
    """Генерация деревни с однонаправленным положением двери и дорог между домами.

    Параметры
    ----------
    house_templates : list
        Список шаблонов домов в специальном формате (из которых генерируется деревня)
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
    seed : int | float | str | bytes | bytearray
        Сид для генерации (None - случайный), по умолчанию None
    """
    if not (attach_dist_minmax[0]<=min_dist<=attach_dist_minmax[1]):
        raise ValueError(f'Минимальное растояние между домами должно быть между attach_dist_minmax: {min_dist}>={attach_dist_minmax[0]} и {min_dist}<={attach_dist_minmax[1]}')
    
    import time #Для отображения длительности генерации)

    generator = Generator_houses(min_dist, attach_dist_minmax[0], attach_dist_minmax[1], max_village_radius=max_village_radius, seed=seed)

    start_t = time.time()
    houses = generator.generate_houses(house_templates, count_house)

    print('Сгенерированно', len(houses), 'домов', round(time.time() - start_t, 2))
    print('Seed', generator.getseed())

    start_r = time.time()
    roads = generate_roads(houses,min_distance,delta_grid_size,shift_diagonally)

    print('Сгенерированно', sum([len(i) for i in roads]), 'дорог', round(time.time() - start_r, 2))
    print('Время генерации:', round(time.time() - start_t, 2))

    return houses, roads
    
if __name__=='__main__':
    
    #Пример

    #Сид случайный
    seed = None

    #Создаём список из 20 случайных домов с шириной по х от 2 до 6 и длиной по у от 1 до 5
    from generate_houses import random_generate_houses_list
    house_templates = random_generate_houses_list(20, [2,6], [2,5], seed=seed)

    #Генерируем деревню из 50 домов с мин растоянием между домами 7; растояние между сгенерированным домом и его предшественником от 7 до 10
    #Минимальным растоянием от дороги до дома 3; Максимальным радиусом деревни 100
    houses, roads = generate_village(house_templates, 50, 7, [7,10],3, max_village_radius=100, shift_diagonally=False, seed=seed)
    
    #Создание .png картинки с маштабом 1:10 (1 блок = 10 пикселей на картинке)
    from vizualization_png import generate_village_image
    generate_village_image(houses, roads, cell_size=10)
    