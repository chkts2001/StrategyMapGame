import random
import math
from .map_data import MapData
import numpy as np

class MountainGenerator:
    def __init__(self, map_data: MapData):
        self.data = map_data


    def generate_multiple_mountain_ranges(self, num_areas=3, size_per_area=150,
                                          peak_percent=0.05, mountain_percent=0.40,
                                          hole_percent=0.30):
        """Генерация гор с настраиваемыми процентами"""

        # Ограничиваем проценты
        peak_percent = max(0.01, min(1.0, peak_percent))
        mountain_percent = max(0.01, min(0.8, mountain_percent))
        hole_percent = max(0.05, min(0.8, hole_percent))

        # Вся карта - равнины
        for y in range(self.data.height):
            for x in range(self.data.width):
                self.data.map[y, x] = 1

        # Добавляем леса
        for y in range(self.data.height):
            for x in range(self.data.width):
                if random.random() < 0.15:
                    self.data.map[y, x] = 2

        total_mountain_cells = 0

        for area_num in range(num_areas):
            print(f"\n🏔️ Горный массив {area_num + 1}:")
            print(
                f"   Настройки: вершины {peak_percent * 100:.0f}%, горы {mountain_percent * 100:.0f}%, дырки {hole_percent * 100:.0f}%")

            center_x = random.randint(self.data.width // 4, 3 * self.data.width // 4)
            center_y = random.randint(self.data.height // 4, 3 * self.data.height // 4)

            target_size = random.randint(size_per_area // 2, size_per_area)

            # СОЗДАЕМ СКЕЛЕТ
            skeleton = set()
            ridge_points = []

            # Основной хребет
            ridge_length = random.randint(target_size // 3, target_size // 2)
            start_angle = random.uniform(0, 2 * math.pi)

            for i in range(ridge_length):
                t = i / ridge_length
                angle_offset = math.sin(t * math.pi * random.uniform(2, 4)) * random.uniform(0.5, 1.5)
                dist = t * ridge_length
                x = int(center_x + math.cos(start_angle + angle_offset) * dist + random.gauss(0, 1))
                y = int(center_y + math.sin(start_angle + angle_offset) * dist + random.gauss(0, 1))
                x = max(0, min(self.data.width - 1, x))
                y = max(0, min(self.data.height - 1, y))
                ridge_points.append((x, y))
                skeleton.add((x, y))

            # Боковые отроги
            branch_points = []
            num_branches = random.randint(3, 6)

            for _ in range(num_branches):
                if len(ridge_points) < 5:
                    break
                start_idx = random.randint(len(ridge_points) // 6, len(ridge_points) * 5 // 6)
                sx, sy = ridge_points[start_idx]

                branch_angle = random.uniform(0, 2 * math.pi)
                branch_length = random.randint(15, 30)

                for i in range(branch_length):
                    x = int(sx + math.cos(branch_angle) * i + random.gauss(0, 2))
                    y = int(sy + math.sin(branch_angle) * i + random.gauss(0, 2))
                    x = max(0, min(self.data.width - 1, x))
                    y = max(0, min(self.data.height - 1, y))
                    branch_points.append((x, y))
                    skeleton.add((x, y))

            # Отдельные вершины
            peak_points = []
            num_peaks = random.randint(3, 6)

            for _ in range(num_peaks):
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(0, target_size // 2)
                x = int(center_x + math.cos(angle) * dist + random.gauss(0, 5))
                y = int(center_y + math.sin(angle) * dist + random.gauss(0, 5))
                x = max(0, min(self.data.width - 1, x))
                y = max(0, min(self.data.height - 1, y))
                peak_points.append((x, y))
                skeleton.add((x, y))

            all_skeleton = ridge_points + branch_points + peak_points

            # ЗАПОЛНЯЕМ ОБЛАСТЬ ВОКРУГ СКЕЛЕТА
            mountain_cells = {}

            for sx, sy in all_skeleton:
                radius = random.randint(5, 8)
                for y in range(sy - radius, sy + radius + 1):
                    for x in range(sx - radius, sx + radius + 1):
                        if self.data.is_valid_cell(x, y):
                            dist = ((x - sx) ** 2 + (y - sy) ** 2) ** 0.5
                            if dist <= radius:
                                if (x, y) not in mountain_cells or mountain_cells[(x, y)] > dist:
                                    mountain_cells[(x, y)] = dist

            # Соединяем точки хребта
            for i in range(len(ridge_points) - 1):
                x1, y1 = ridge_points[i]
                x2, y2 = ridge_points[i + 1]
                steps = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5) + 1
                for step in range(steps):
                    t = step / steps
                    x = int(x1 + t * (x2 - x1))
                    y = int(y1 + t * (y2 - y1))
                    if self.data.is_valid_cell(x, y):
                        if (x, y) not in mountain_cells:
                            mountain_cells[(x, y)] = 2

            # ============ ПРИМЕНЯЕМ ПРОЦЕНТ ДЫРОК ============
            cells_list = list(mountain_cells.keys())

            for x, y in cells_list:
                dist_to_skeleton = mountain_cells.get((x, y), 100)

                # Разная вероятность дырок в зависимости от расстояния до скелета
                if dist_to_skeleton < 3:
                    # Ядро - меньше дырок
                    if random.random() < hole_percent * 0.5:
                        del mountain_cells[(x, y)]
                elif dist_to_skeleton < 6:
                    # Средняя зона - средние дырки
                    if random.random() < hole_percent:
                        del mountain_cells[(x, y)]
                else:
                    # Края - больше дырок
                    if random.random() < hole_percent * 1.5:
                        del mountain_cells[(x, y)]

            # ============ РАЗМЕЩАЕМ ГОРЫ С НАСТРАИВАЕМЫМИ ПРОЦЕНТАМИ ============
            cells_added = 0

            # Сначала собираем все клетки для подсчета
            temp_cells = []
            for (x, y), dist_to_skeleton in mountain_cells.items():
                if self.data.map[y, x] in [1, 2]:
                    temp_cells.append((x, y, dist_to_skeleton))

            # Корректируем проценты для этого массива
            temp_cells.sort(key=lambda cell: cell[2])  # сортируем по расстоянию

            total_cells = len(temp_cells)
            peak_count_target = int(total_cells * peak_percent)
            mountain_count_target = int(total_cells * mountain_percent)

            # Распределяем типы
            for i, (x, y, dist) in enumerate(temp_cells):
                if i < peak_count_target:
                    # Вершины
                    self.data.map[y, x] = 7
                elif i < peak_count_target + mountain_count_target:
                    # Обычные горы
                    if random.random() < 0.7:
                        self.data.map[y, x] = 3
                    else:
                        self.data.map[y, x] = 12  # высокие горы
                else:
                    # Остальное - низкие горы, предгорья, холмы
                    if dist < 5:
                        self.data.map[y, x] = 11  # низкие горы
                    elif dist < 8:
                        self.data.map[y, x] = 10  # предгорья
                    else:
                        self.data.map[y, x] = 8  # холмы

                cells_added += 1

            total_mountain_cells += cells_added

            # Статистика
            peak_actual = sum(1 for x, y in mountain_cells if self.data.map[y, x] == 7)
            mountain_actual = sum(1 for x, y in mountain_cells if self.data.map[y, x] in [3, 12])
            other_actual = sum(1 for x, y in mountain_cells if self.data.map[y, x] in [11, 10, 8])
            hole_actual = len(mountain_cells) - cells_added

            print(f"   Результаты:")
            print(f"   - Вершины: {peak_actual} ({peak_actual / len(mountain_cells) * 100:.1f}%)")
            print(f"   - Горы: {mountain_actual} ({mountain_actual / len(mountain_cells) * 100:.1f}%)")
            print(f"   - Холмы/предгорья: {other_actual} ({other_actual / len(mountain_cells) * 100:.1f}%)")
            print(f"   - Дырки: {hole_actual} клеток")

        print(f"\n✅ Всего гор: {total_mountain_cells} клеток")


    def generate_mountain_range(self, scale=50.0, octaves=6, center_x=None, center_y=None,
                                size=100, num_areas=3, max_cells_per_area=150):
        """Горы как СПЛОШНЫЕ пятна (старый метод)"""
        if center_x is None:
            center_x = self.data.width // 2
        if center_y is None:
            center_y = self.data.height // 2

        # Сначала делаем всю карту равниной
        for y in range(self.data.height):
            for x in range(self.data.width):
                self.data.map[y, x] = 1
                self.data.height_map[y, x] = 0.5

        # Добавляем леса случайно
        for y in range(self.data.height):
            for x in range(self.data.width):
                if random.random() < 0.2:
                    self.data.map[y, x] = 2

        # Генерируем горные массивы
        for area in range(num_areas):
            # Центр горного массива
            area_x = center_x + random.randint(-size, size)
            area_y = center_y + random.randint(-size, size)
            area_x = max(0, min(self.data.width - 1, area_x))
            area_y = max(0, min(self.data.height - 1, area_y))

            # Размер массива (радиус в клетках)
            radius = random.randint(15, 35)

            # ЗАПОЛНЯЕМ СПЛОШНОЙ КРУГ (или эллипс)
            mountain_cells = []

            # Растягиваем форму (эллипс)
            rx = radius * random.uniform(0.7, 1.3)
            ry = radius * random.uniform(0.7, 1.3)

            # Заполняем ВСЕ клетки внутри эллипса
            for y in range(int(area_y - ry), int(area_y + ry) + 1):
                for x in range(int(area_x - rx), int(area_x + rx) + 1):
                    if self.data.is_valid_cell(x, y):
                        # Проверяем, внутри ли эллипса
                        if ((x - area_x) ** 2 / (rx ** 2) +
                            (y - area_y) ** 2 / (ry ** 2)) <= 1:
                            mountain_cells.append((x, y))

            # Добавляем "выступы" для более естественной формы
            for _ in range(random.randint(5, 15)):
                angle = random.uniform(0, 2 * math.pi)
                length = random.randint(5, 15)
                for i in range(length):
                    x = int(area_x + (rx + i * 0.5) * math.cos(angle))
                    y = int(area_y + (ry + i * 0.5) * math.sin(angle))
                    if self.data.is_valid_cell(x, y):
                        mountain_cells.append((x, y))

            # Преобразуем в множество для уникальности
            mountain_cells = list(set(mountain_cells))

            # Ограничиваем количество клеток
            if len(mountain_cells) > max_cells_per_area:
                mountain_cells = mountain_cells[:max_cells_per_area]

            # Размещаем горы (сплошным пятном)
            for x, y in mountain_cells:
                if self.data.map[y, x] == 1 or self.data.map[y, x] == 2:  # только на равнинах и лесах
                    # Разная высота: центр выше, края ниже
                    dist_to_center = ((x - area_x) ** 2 + (y - area_y) ** 2) ** 0.5
                    if dist_to_center < radius * 0.3:
                        self.data.map[y, x] = 7  # вершина (снег) в центре
                    else:
                        self.data.map[y, x] = 3  # гора
                    self.data.height_map[y, x] = 0.8

            print(f"🏔️ Горный массив {area + 1}: {len(mountain_cells)} клеток (радиус {radius})")

        mountain_count = np.sum((self.data.map == 3) | (self.data.map == 7))
        print(f"✅ Всего гор: {mountain_count} клеток")


