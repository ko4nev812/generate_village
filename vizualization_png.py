from PIL import Image, ImageDraw
import random
import hashlib
personal_colors = {
    1000: (10,10,10),
    1001: (10,256,10),
    1002: (256,256,10)
}
def get_house_color(house_id):
        if house_id in personal_colors: return personal_colors[house_id]
        # Используем хеш для детерминированной генерации цвета
        hash_obj = hashlib.md5(str(house_id).encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        # Генерируем цвет в приятном диапазоне (не слишком темный/светлый)
        r = (hash_int % 128) + 64
        g = ((hash_int >> 8) % 128) + 64
        b = ((hash_int >> 16) % 128) + 64
        
        return (r, g, b)
def generate_village_image(houses, roads, output_file="village.png", cell_size=20):
    """
    Генерирует изображение деревни с домами и дорогами (дорожные блоки)
    """
    # 1. Определяем границы изображения
    all_points = []
    for house in houses:
        x, y, w, h, _, id_houses = house
        all_points.extend([(x, y), (x+w, y+h)])
    for road in roads:
        all_points.extend(road)
    
    if not all_points:
        return
    
    min_x = min(p[0] for p in all_points)
    max_x = max(p[0] for p in all_points)
    min_y = min(p[1] for p in all_points)
    max_y = max(p[1] for p in all_points)
    
    # Добавляем отступы
    padding = 2
    min_x -= padding
    max_x += padding
    min_y -= padding
    max_y += padding
    
    # 2. Создаем изображение
    width = (max_x - min_x + 1) * cell_size
    height = (max_y - min_y + 1) * cell_size
    print((width, height))
    img = Image.new('RGB', (width, height), (255, 255, 255))

    draw = ImageDraw.Draw(img)
    
    # 3. Функция для преобразования координат
    def to_pixel(x, y):
        px = (x - min_x) * cell_size
        py = (max_y - y) * cell_size  # Инвертируем Y
        return px, py
    
    
    
    
    # 5. Рисуем дома
    for house in houses:
        x, y, w, h, door, house_id = house
        
        # Координаты дома в пикселях
        x1, y1 = to_pixel(x, y)
        x2, y2 = to_pixel(x + w, y + h)
        
        # Упорядочиваем координаты
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        
        # Рисуем дом
        draw.rectangle(
            [x1, y1, x2 - 1, y2 - 1],
            fill=get_house_color(house_id),
            outline=(0, 0, 0)
        )
        
        # Рисуем дверь
        door_x = x + door - 1
        door_px, door_py = to_pixel(door_x, y)
        draw.rectangle(
            [door_px, door_py - cell_size//2 - 1, door_px + cell_size - 1, door_py],
            fill=(160, 0, 0),
            outline=(0, 0, 0))
    # 4. Рисуем дороги (блоками)
    for road in roads:
        for x, y in road:
            px, py = to_pixel(x, y)
            draw.rectangle(
                [px, py, px + cell_size - 1, py + cell_size - 1],
                fill=(120, 120, 120),
                outline=(80, 80, 80)
            )
    # 6. Сохраняем изображение
    img.save(output_file)
    print(f"Изображение сохранено как {output_file}")