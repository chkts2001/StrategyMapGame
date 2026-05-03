import numpy as np
import random
from perlin_noise import PerlinNoise

import numpy as np
import random
import math
from perlin_noise import PerlinNoise
from .map_data import MapData
from .generate_cities import CityGenerator
from .generate_montains import MountainGenerator
from .generate_rivers import RiverGenerator


class GameMap:
    def __init__(self, width, height):
        # Создаем общий контейнер данных
        self.data = MapData(width, height)

        # Создаем генераторы
        self.mountain_gen = MountainGenerator(self.data)
        self.river_gen = RiverGenerator(self.data)
        self.city_gen = CityGenerator(self.data)

    def generate_perlin(self, scale=50.0, octaves=6, persistence=0.5, lacunarity=2.0):
        """Генерация карты ПОЛНОСТЬЮ БЕЗ ВОДЫ"""

        noise_gen = PerlinNoise(octaves=octaves, seed=random.randint(0, 10000))

        min_val = float('inf')
        max_val = float('-inf')
        temp_values = []

        # Сначала собираем все значения
        for y in range(self.data.height):
            for x in range(self.data.width):
                nx = x / scale
                ny = y / scale
                value = noise_gen([nx, ny])
                temp_values.append(value)
                min_val = min(min_val, value)
                max_val = max(max_val, value)

        # Нормализуем и заполняем карту
        for y in range(self.data.height):
            for x in range(self.data.width):
                nx = x / scale
                ny = y / scale
                value = noise_gen([nx, ny])

                # Нормализация от 0 до 1
                if max_val != min_val:
                    normalized = (value - min_val) / (max_val - min_val)
                else:
                    normalized = 0.5

                # ПОДНИМАЕМ МИНИМАЛЬНОЕ ЗНАЧЕНИЕ (убираем воду)
                normalized = normalized * 0.8 + 0.2  # теперь диапазон 0.2 - 1.0

                # Преобразуем в тип местности (ТОЛЬКО СУША)
                if normalized < 0.35:
                    self.data.map[y, x] = 0  # равнина/

    def generate_rivers(self, num_rivers=5):
        """Генерация рек"""
        return self.river_gen.generate_rivers(num_rivers)

# class GameMap:
#     def __init__(self, width, height):
#         self.width = width
#         self.height = height
#         self.map = np.zeros((height, width), dtype=int)
#         self.cities = []
#         self.resources = np.zeros((height, width), dtype=int)
#         self.moisture = np.zeros((height, width))  # карта влажности
#         self.height_map = np.zeros((self.height, self.width))  # карта высот
#
#     def generate_perlin(self, scale=50.0, octaves=6, persistence=0.5, lacunarity=2.0):
#         """Генерация карты ПОЛНОСТЬЮ БЕЗ ВОДЫ"""
#
#         noise_gen = PerlinNoise(octaves=octaves, seed=random.randint(0, 10000))
#
#         min_val = float('inf')
#         max_val = float('-inf')
#         temp_values = []
#
#         # Сначала собираем все значения
#         for y in range(self.height):
#             for x in range(self.width):
#                 nx = x / scale
#                 ny = y / scale
#                 value = noise_gen([nx, ny])
#                 temp_values.append(value)
#                 min_val = min(min_val, value)
#                 max_val = max(max_val, value)
#
#         # Нормализуем и заполняем карту
#         for y in range(self.height):
#             for x in range(self.width):
#                 nx = x / scale
#                 ny = y / scale
#                 value = noise_gen([nx, ny])
#
#                 # Нормализация от 0 до 1
#                 if max_val != min_val:
#                     normalized = (value - min_val) / (max_val - min_val)
#                 else:
#                     normalized = 0.5
#
#                 # ПОДНИМАЕМ МИНИМАЛЬНОЕ ЗНАЧЕНИЕ (убираем воду)
#                 # Сдвигаем весь диапазон вверх, чтобы минимальное стало 0.2
#                 normalized = normalized * 0.8 + 0.2  # теперь диапазон 0.2 - 1.0
#
#                 # Преобразуем в тип местности (ТОЛЬКО СУША)
#                 if normalized < 0.35:
#                     self.map[y, x] = 0  # равнина/низменность
#                 elif normalized < 0.55:
#                     self.map[y, x] = 1  # равнина
#                 elif normalized < 0.75:
#                     self.map[y, x] = 2  # лес
#                 elif normalized < 0.9:
#                     self.map[y, x] = 3  # горы
#                 else:
#                     self.map[y, x] = 7  # песок/вершины
#
#                 self.height_map[y, x] = normalized
#                 self.moisture[y, x] = 0.5
#
#     def add_rivers(self, num_rivers=3, source_percent=0.3, buffer_size=5):
#         """Добавляет реки, где указанный процент рек начинается с истоков (в горах)"""
#
#         if not hasattr(self, 'river_cells'):
#             self.river_cells = set()
#
#         # Для хранения расширенной буферной зоны (включая будущие реки)
#         if not hasattr(self, 'river_buffer_zones'):
#             self.river_buffer_zones = set()
#
#         # Вычисляем количество рек с истоками (округляем в меньшую сторону)
#         num_source_rivers = int(num_rivers * source_percent)
#         num_edge_rivers = num_rivers - num_source_rivers
#
#         print(f"📊 Планируется рек: {num_rivers}")
#         print(f"   - С истоками в горах: {num_source_rivers}")
#         print(f"   - С края карты: {num_edge_rivers}")
#         print(f"   - Буферная зона: {buffer_size} клеток")
#
#         rivers_added = 0
#         source_rivers_added = 0
#         edge_rivers_added = 0
#
#         # Сначала добавляем реки с истоками
#         for _ in range(num_source_rivers):
#             success = self._add_single_river_with_source_improved(
#                 river_num=rivers_added + 1,
#                 buffer_size=buffer_size
#             )
#             if success:
#                 rivers_added += 1
#                 source_rivers_added += 1
#
#         # Затем добавляем реки с края карты
#         for _ in range(num_edge_rivers):
#             success = self._add_single_river_from_edge_improved(
#                 river_num=rivers_added + 1,
#                 buffer_size=buffer_size
#             )
#             if success:
#                 rivers_added += 1
#                 edge_rivers_added += 1
#
#         print(f"\n✅ ИТОГО добавлено рек: {rivers_added}")
#         print(f"   - С истоками: {source_rivers_added}")
#         print(f"   - С края: {edge_rivers_added}")
#
#         return rivers_added
#
#     def _add_single_river_with_source_improved(self, river_num, buffer_size=5):
#         """Добавляет одну реку с истоком (с проверкой буфера на каждом шаге)"""
#
#         attempts = 0
#         max_attempts = 50
#
#         while attempts < max_attempts:
#             # Ищем подходящий исток
#             source_candidates = []
#
#             for y in range(self.height):
#                 for x in range(self.width):
#                     if self.map[y][x] in [3, 7, 8, 10, 11, 12]:
#                         # Проверяем буферную зону
#                         if (x, y) not in self.river_cells and (x, y) not in self.river_buffer_zones:
#                             source_candidates.append((x, y))
#
#             if not source_candidates:
#                 print(f"⚠️ Не найдено места для истока реки {river_num}")
#                 return False
#
#             source_x, source_y = random.choice(source_candidates)
#
#             # Начальное направление
#             directions = [(0, 1), (1, 1), (-1, 1), (1, 0), (-1, 0)]
#             dx, dy = random.choice(directions)
#
#             # Создаем реку с проверкой буфера
#             river_cells = []
#             visited = set()
#             current_x, current_y = source_x, source_y
#             steps = 0
#             max_steps = max(self.width, self.height)
#             valid = True
#
#             while 0 <= current_x < self.width and 0 <= current_y < self.height and steps < max_steps:
#                 # Проверка на самопересечение
#                 if (current_x, current_y) in visited:
#                     valid = False
#                     break
#
#                 # Проверка на другие реки и их буферные зоны
#                 if (current_x, current_y) in self.river_cells:
#                     valid = False
#                     break
#
#                 # ГЛАВНОЕ: проверка буферной зоны других рек
#                 if (current_x, current_y) in self.river_buffer_zones:
#                     valid = False
#                     break
#
#                 visited.add((current_x, current_y))
#                 river_cells.append((current_x, current_y))
#
#                 # Плавная смена направления
#                 if steps > 3 and random.random() < 0.15:
#                     possible_dirs = self._get_smooth_directions(dx, dy, current_x, current_y, visited)
#                     if possible_dirs:
#                         # Дополнительно проверяем новое направление на буфер
#                         for ndx, ndy in possible_dirs:
#                             test_x = current_x + ndx
#                             test_y = current_y + ndy
#                             if 0 <= test_x < self.width and 0 <= test_y < self.height:
#                                 if (test_x, test_y) not in self.river_buffer_zones:
#                                     dx, dy = ndx, ndy
#                                     break
#
#                 current_x += dx
#                 current_y += dy
#                 steps += 1
#
#                 # Защита от бесконечного цикла
#                 if steps > max_steps * 2:
#                     valid = False
#                     break
#
#             if valid and len(river_cells) > 15:
#                 # Добавляем реку
#                 for rx, ry in river_cells:
#                     if self.map[ry][rx] != 5:
#                         self.map[ry][rx] = 4
#                         self.river_cells.add((rx, ry))
#
#                 # Добавляем буферную зону
#                 for rx, ry in river_cells:
#                     for by in range(-buffer_size, buffer_size + 1):
#                         for bx in range(-buffer_size, buffer_size + 1):
#                             bx2, by2 = rx + bx, ry + by
#                             if 0 <= bx2 < self.width and 0 <= by2 < self.height:
#                                 self.river_buffer_zones.add((bx2, by2))
#
#                 print(f"✓ Река {river_num} (с истоком): {len(river_cells)} клеток, исток в ({source_x}, {source_y})")
#                 return True
#
#             attempts += 1
#
#         print(f"⚠️ Не удалось создать реку {river_num} с истоком")
#         return False
#
#     def _get_smooth_directions(self, dx, dy, x, y, visited):
#         """Возвращает список плавных направлений для продолжения реки"""
#
#         # Базовые плавные переходы
#         smooth_map = {
#             (0, 1): [(0, 1), (1, 1), (-1, 1)],
#             (0, -1): [(0, -1), (1, -1), (-1, -1)],
#             (1, 0): [(1, 0), (1, 1), (1, -1)],
#             (-1, 0): [(-1, 0), (-1, 1), (-1, -1)],
#             (1, 1): [(1, 1), (1, 0), (0, 1)],
#             (-1, 1): [(-1, 1), (-1, 0), (0, 1)],
#             (1, -1): [(1, -1), (1, 0), (0, -1)],
#             (-1, -1): [(-1, -1), (-1, 0), (0, -1)],
#         }
#
#         allowed = smooth_map.get((dx, dy), [(dx, dy)])
#
#         # Фильтруем направления
#         result = []
#         for ndx, ndy in allowed:
#             test_x = x + ndx
#             test_y = y + ndy
#             if 0 <= test_x < self.width and 0 <= test_y < self.height:
#                 if (test_x, test_y) not in visited:
#                     result.append((ndx, ndy))
#
#         return result
#
#     def _add_single_river_from_edge_improved(self, river_num, buffer_size=5):
#         """Добавляет реку с края карты (с проверкой буфера на каждом шаге)"""
#
#         attempts = 0
#         max_attempts = 50
#
#         while attempts < max_attempts:
#             # Выбираем сторону старта
#             side = random.choice(['top', 'bottom', 'left', 'right'])
#
#             if side == 'top':
#                 x = random.randint(0, self.width - 1)
#                 y = 0
#                 dx = random.choice([-1, 0, 1])
#                 dy = 1
#             elif side == 'bottom':
#                 x = random.randint(0, self.width - 1)
#                 y = self.height - 1
#                 dx = random.choice([-1, 0, 1])
#                 dy = -1
#             elif side == 'left':
#                 x = 0
#                 y = random.randint(0, self.height - 1)
#                 dx = 1
#                 dy = random.choice([-1, 0, 1])
#             else:
#                 x = self.width - 1
#                 y = random.randint(0, self.height - 1)
#                 dx = -1
#                 dy = random.choice([-1, 0, 1])
#
#             # Проверяем стартовую точку (буферная зона других рек)
#             if (x, y) in self.river_cells or (x, y) in self.river_buffer_zones:
#                 attempts += 1
#                 continue
#
#             # Создаем реку
#             river_cells = []
#             visited = set()
#             current_x, current_y = x, y
#             valid = True
#             steps = 0
#             max_steps = max(self.width, self.height)
#
#             while 0 <= current_x < self.width and 0 <= current_y < self.height and steps < max_steps:
#                 # Проверки
#                 if (current_x, current_y) in visited:
#                     valid = False
#                     break
#
#                 if (current_x, current_y) in self.river_cells:
#                     valid = False
#                     break
#
#                 # Проверка буферной зоны
#                 if (current_x, current_y) in self.river_buffer_zones:
#                     valid = False
#                     break
#
#                 visited.add((current_x, current_y))
#                 river_cells.append((current_x, current_y))
#
#                 if steps > 3 and random.random() < 0.15:
#                     possible_dirs = self._get_smooth_directions(dx, dy, current_x, current_y, visited)
#                     if possible_dirs:
#                         for ndx, ndy in possible_dirs:
#                             test_x = current_x + ndx
#                             test_y = current_y + ndy
#                             if 0 <= test_x < self.width and 0 <= test_y < self.height:
#                                 if (test_x, test_y) not in self.river_buffer_zones:
#                                     dx, dy = ndx, ndy
#                                     break
#
#                 current_x += dx
#                 current_y += dy
#                 steps += 1
#
#                 if steps > max_steps * 2:
#                     valid = False
#                     break
#
#             if valid and len(river_cells) > 20:
#                 for rx, ry in river_cells:
#                     if self.map[ry][rx] != 5:
#                         self.map[ry][rx] = 4
#                         self.river_cells.add((rx, ry))
#
#                 # Добавляем буферную зону
#                 for rx, ry in river_cells:
#                     for by in range(-buffer_size, buffer_size + 1):
#                         for bx in range(-buffer_size, buffer_size + 1):
#                             bx2, by2 = rx + bx, ry + by
#                             if 0 <= bx2 < self.width and 0 <= by2 < self.height:
#                                 self.river_buffer_zones.add((bx2, by2))
#
#                 print(f"✓ Река {river_num} (с края): {len(river_cells)} клеток, старт {side}")
#                 return True
#
#             attempts += 1
#
#         print(f"⚠️ Не удалось создать реку {river_num} с края")
#         return False
#
#     def generate_mountain_range(self, scale=50.0, octaves=6, center_x=None, center_y=None,
#                                 size=100, num_areas=3, max_cells_per_area=150):
#         """Горы как СПЛОШНЫЕ пятна"""
#
#         if center_x is None:
#             center_x = self.width // 2
#         if center_y is None:
#             center_y = self.height // 2
#
#         # Сначала делаем всю карту равниной
#         for y in range(self.height):
#             for x in range(self.width):
#                 self.map[y, x] = 1
#                 self.height_map[y, x] = 0.5
#
#         # Добавляем леса случайно
#         for y in range(self.height):
#             for x in range(self.width):
#                 if random.random() < 0.2:
#                     self.map[y, x] = 2
#
#         # Генерируем горные массивы
#         for area in range(num_areas):
#             # Центр горного массива
#             area_x = center_x + random.randint(-size, size)
#             area_y = center_y + random.randint(-size, size)
#             area_x = max(0, min(self.width - 1, area_x))
#             area_y = max(0, min(self.height - 1, area_y))
#
#             # Размер массива (радиус в клетках)
#             radius = random.randint(15, 35)
#
#             # ЗАПОЛНЯЕМ СПЛОШНОЙ КРУГ (или эллипс)
#             mountain_cells = []
#
#             # Растягиваем форму (эллипс)
#             rx = radius * random.uniform(0.7, 1.3)
#             ry = radius * random.uniform(0.7, 1.3)
#
#             # Заполняем ВСЕ клетки внутри эллипса
#             for y in range(int(area_y - ry), int(area_y + ry) + 1):
#                 for x in range(int(area_x - rx), int(area_x + rx) + 1):
#                     if 0 <= x < self.width and 0 <= y < self.height:
#                         # Проверяем, внутри ли эллипса
#                         if ((x - area_x) ** 2 / (rx ** 2) +
#                             (y - area_y) ** 2 / (ry ** 2)) <= 1:
#                             mountain_cells.append((x, y))
#
#             # Добавляем "выступы" для более естественной формы
#             for _ in range(random.randint(5, 15)):
#                 angle = random.uniform(0, 2 * math.pi)
#                 length = random.randint(5, 15)
#                 for i in range(length):
#                     x = int(area_x + (rx + i * 0.5) * math.cos(angle))
#                     y = int(area_y + (ry + i * 0.5) * math.sin(angle))
#                     if 0 <= x < self.width and 0 <= y < self.height:
#                         mountain_cells.append((x, y))
#
#             # Преобразуем в множество для уникальности
#             mountain_cells = list(set(mountain_cells))
#
#             # Ограничиваем количество клеток
#             if len(mountain_cells) > max_cells_per_area:
#                 mountain_cells = mountain_cells[:max_cells_per_area]
#
#             # Размещаем горы (сплошным пятном)
#             for x, y in mountain_cells:
#                 if self.map[y, x] == 1 or self.map[y, x] == 2:  # только на равнинах и лесах
#                     # Разная высота: центр выше, края ниже
#                     dist_to_center = ((x - area_x) ** 2 + (y - area_y) ** 2) ** 0.5
#                     if dist_to_center < radius * 0.3:
#                         self.map[y, x] = 7  # вершина (снег) в центре
#                     else:
#                         self.map[y, x] = 3  # гора
#                     self.height_map[y, x] = 0.8
#
#             print(f"🏔️ Горный массив {area + 1}: {len(mountain_cells)} клеток (радиус {radius})")
#
#         mountain_count = np.sum((self.map == 3) | (self.map == 7))
#         print(f"✅ Всего гор: {mountain_count} клеток")
#
#     def generate_multiple_mountain_ranges(self, num_areas=3, size_per_area=150,
#                                           peak_percent=0.05, mountain_percent=0.40,
#                                           hole_percent=0.30):
#         """Генерация гор с настраиваемыми процентами
#
#         Args:
#             num_areas: количество горных массивов
#             size_per_area: примерный размер массива
#             peak_percent: процент вершин (0.01 - 0.15, по умолчанию 0.05 = 5%)
#             mountain_percent: процент обычных гор (0.20 - 0.60, по умолчанию 0.40 = 40%)
#             hole_percent: процент дырок (0.10 - 0.70, по умолчанию 0.30 = 30%)
#         """
#
#         # Ограничиваем проценты
#         peak_percent = max(0.01, min(1.0, peak_percent))
#         mountain_percent = max(0.01, min(0.8, mountain_percent))
#         hole_percent = max(0.05, min(0.8, hole_percent))
#
#         # Вся карта - равнины
#         for y in range(self.height):
#             for x in range(self.width):
#                 self.map[y, x] = 1
#
#         # Добавляем леса
#         for y in range(self.height):
#             for x in range(self.width):
#                 if random.random() < 0.15:
#                     self.map[y, x] = 2
#
#         total_mountain_cells = 0
#
#         for area_num in range(num_areas):
#             print(f"\n🏔️ Горный массив {area_num + 1}:")
#             print(
#                 f"   Настройки: вершины {peak_percent * 100:.0f}%, горы {mountain_percent * 100:.0f}%, дырки {hole_percent * 100:.0f}%")
#
#             center_x = random.randint(self.width // 4, 3 * self.width // 4)
#             center_y = random.randint(self.height // 4, 3 * self.height // 4)
#
#             target_size = random.randint(size_per_area // 2, size_per_area)
#
#             # СОЗДАЕМ СКЕЛЕТ
#             skeleton = set()
#             ridge_points = []
#
#             # Основной хребет
#             ridge_length = random.randint(target_size // 3, target_size // 2)
#             start_angle = random.uniform(0, 2 * math.pi)
#
#             for i in range(ridge_length):
#                 t = i / ridge_length
#                 angle_offset = math.sin(t * math.pi * random.uniform(2, 4)) * random.uniform(0.5, 1.5)
#                 dist = t * ridge_length
#                 x = int(center_x + math.cos(start_angle + angle_offset) * dist + random.gauss(0, 1))
#                 y = int(center_y + math.sin(start_angle + angle_offset) * dist + random.gauss(0, 1))
#                 x = max(0, min(self.width - 1, x))
#                 y = max(0, min(self.height - 1, y))
#                 ridge_points.append((x, y))
#                 skeleton.add((x, y))
#
#             # Боковые отроги
#             branch_points = []
#             num_branches = random.randint(3, 6)
#
#             for _ in range(num_branches):
#                 if len(ridge_points) < 5:
#                     break
#                 start_idx = random.randint(len(ridge_points) // 6, len(ridge_points) * 5 // 6)
#                 sx, sy = ridge_points[start_idx]
#
#                 branch_angle = random.uniform(0, 2 * math.pi)
#                 branch_length = random.randint(15, 30)
#
#                 for i in range(branch_length):
#                     x = int(sx + math.cos(branch_angle) * i + random.gauss(0, 2))
#                     y = int(sy + math.sin(branch_angle) * i + random.gauss(0, 2))
#                     x = max(0, min(self.width - 1, x))
#                     y = max(0, min(self.height - 1, y))
#                     branch_points.append((x, y))
#                     skeleton.add((x, y))
#
#             # Отдельные вершины
#             peak_points = []
#             num_peaks = random.randint(3, 6)
#
#             for _ in range(num_peaks):
#                 angle = random.uniform(0, 2 * math.pi)
#                 dist = random.uniform(0, target_size // 2)
#                 x = int(center_x + math.cos(angle) * dist + random.gauss(0, 5))
#                 y = int(center_y + math.sin(angle) * dist + random.gauss(0, 5))
#                 x = max(0, min(self.width - 1, x))
#                 y = max(0, min(self.height - 1, y))
#                 peak_points.append((x, y))
#                 skeleton.add((x, y))
#
#             all_skeleton = ridge_points + branch_points + peak_points
#
#             # ЗАПОЛНЯЕМ ОБЛАСТЬ ВОКРУГ СКЕЛЕТА
#             mountain_cells = {}
#
#             for sx, sy in all_skeleton:
#                 radius = random.randint(5, 8)
#                 for y in range(sy - radius, sy + radius + 1):
#                     for x in range(sx - radius, sx + radius + 1):
#                         if 0 <= x < self.width and 0 <= y < self.height:
#                             dist = ((x - sx) ** 2 + (y - sy) ** 2) ** 0.5
#                             if dist <= radius:
#                                 if (x, y) not in mountain_cells or mountain_cells[(x, y)] > dist:
#                                     mountain_cells[(x, y)] = dist
#
#             # Соединяем точки хребта
#             for i in range(len(ridge_points) - 1):
#                 x1, y1 = ridge_points[i]
#                 x2, y2 = ridge_points[i + 1]
#                 steps = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5) + 1
#                 for step in range(steps):
#                     t = step / steps
#                     x = int(x1 + t * (x2 - x1))
#                     y = int(y1 + t * (y2 - y1))
#                     if 0 <= x < self.width and 0 <= y < self.height:
#                         if (x, y) not in mountain_cells:
#                             mountain_cells[(x, y)] = 2
#
#             # ============ ПРИМЕНЯЕМ ПРОЦЕНТ ДЫРОК ============
#             cells_list = list(mountain_cells.keys())
#
#             for x, y in cells_list:
#                 dist_to_skeleton = mountain_cells.get((x, y), 100)
#
#                 # Разная вероятность дырок в зависимости от расстояния до скелета
#                 if dist_to_skeleton < 3:
#                     # Ядро - меньше дырок
#                     if random.random() < hole_percent * 0.5:
#                         del mountain_cells[(x, y)]
#                 elif dist_to_skeleton < 6:
#                     # Средняя зона - средние дырки
#                     if random.random() < hole_percent:
#                         del mountain_cells[(x, y)]
#                 else:
#                     # Края - больше дырок
#                     if random.random() < hole_percent * 1.5:
#                         del mountain_cells[(x, y)]
#
#             # ============ РАЗМЕЩАЕМ ГОРЫ С НАСТРАИВАЕМЫМИ ПРОЦЕНТАМИ ============
#             cells_added = 0
#
#             # Сначала собираем все клетки для подсчета
#             temp_cells = []
#             for (x, y), dist_to_skeleton in mountain_cells.items():
#                 if self.map[y, x] in [1, 2]:
#                     temp_cells.append((x, y, dist_to_skeleton))
#
#             # Корректируем проценты для этого массива
#             # Вершины - только на самых близких к скелету клетках
#             temp_cells.sort(key=lambda cell: cell[2])  # сортируем по расстоянию
#
#             total_cells = len(temp_cells)
#             peak_count_target = int(total_cells * peak_percent)
#             mountain_count_target = int(total_cells * mountain_percent)
#
#             # Распределяем типы
#             for i, (x, y, dist) in enumerate(temp_cells):
#                 if i < peak_count_target:
#                     # Вершины
#                     self.map[y, x] = 7
#                 elif i < peak_count_target + mountain_count_target:
#                     # Обычные горы
#                     if random.random() < 0.7:
#                         self.map[y, x] = 3
#                     else:
#                         self.map[y, x] = 12  # высокие горы
#                 else:
#                     # Остальное - низкие горы, предгорья, холмы
#                     if dist < 5:
#                         self.map[y, x] = 11  # низкие горы
#                     elif dist < 8:
#                         self.map[y, x] = 10  # предгорья
#                     else:
#                         self.map[y, x] = 8  # холмы
#
#                 cells_added += 1
#
#             total_mountain_cells += cells_added
#
#             # Статистика
#             peak_actual = sum(1 for x, y in mountain_cells if self.map[y, x] == 7)
#             mountain_actual = sum(1 for x, y in mountain_cells if self.map[y, x] in [3, 12])
#             other_actual = sum(1 for x, y in mountain_cells if self.map[y, x] in [11, 10, 8])
#             hole_actual = len(mountain_cells) - cells_added
#
#             print(f"   Результаты:")
#             print(f"   - Вершины: {peak_actual} ({peak_actual / len(mountain_cells) * 100:.1f}%)")
#             print(f"   - Горы: {mountain_actual} ({mountain_actual / len(mountain_cells) * 100:.1f}%)")
#             print(f"   - Холмы/предгорья: {other_actual} ({other_actual / len(mountain_cells) * 100:.1f}%)")
#             print(f"   - Дырки: {hole_actual} клеток")
#
#         print(f"\n✅ Всего гор: {total_mountain_cells} клеток")
#
#     def add_cities_random_shapes(self, num_cities=10, min_size=1, max_size=40):
#         """Генерация городов случайных форм от 1 до 40 клеток"""
#
#         self.cities = []
#         occupied = set()  # Запоминаем занятые клетки
#
#         for city_num in range(num_cities):
#             target_size = random.randint(min_size, max_size)
#
#             # Ищем подходящий центр
#             attempts = 0
#             placed = False
#
#             while not placed and attempts < 200:
#                 # Случайный центр
#                 center_x = random.randint(5, self.width - 5)
#                 center_y = random.randint(5, self.height - 5)
#
#                 # Центр не должен быть на воде, горах или реке
#                 if self.map[center_y, center_x] in [0, 3, 4, 6]:
#                     attempts += 1
#                     continue
#
#                 # Создаем случайную форму
#                 city_cells = set()
#                 city_cells.add((center_x, center_y))
#
#                 # Алгоритм случайного роста (как снежинка)
#                 current_size = 1
#                 growth_attempts = 0
#
#                 while current_size < target_size and growth_attempts < target_size * 5:
#                     # Выбираем случайную клетку из уже добавленных
#                     if not city_cells:
#                         break
#
#                     source_cell = random.choice(list(city_cells))
#                     sx, sy = source_cell
#
#                     # Случайное направление для новой клетки
#                     dx = random.choice([-1, 0, 1])
#                     dy = random.choice([-1, 0, 1])
#
#                     # Пропускаем нулевое направление (оставаться на месте)
#                     if dx == 0 and dy == 0:
#                         growth_attempts += 1
#                         continue
#
#                     new_x = sx + dx
#                     new_y = sy + dy
#
#                     # Проверяем границы
#                     if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
#                         growth_attempts += 1
#                         continue
#
#                     # Проверяем, не занято ли
#                     if (new_x, new_y) in occupied:
#                         growth_attempts += 1
#                         continue
#
#                     # Проверяем, подходит ли местность
#                     if self.map[new_y, new_x] in [0, 3, 4, 6]:  # вода, горы, реки
#                         growth_attempts += 1
#                         continue
#
#                     # Добавляем новую клетку
#                     if (new_x, new_y) not in city_cells:
#                         city_cells.add((new_x, new_y))
#                         current_size += 1
#                         growth_attempts = 0
#                     else:
#                         growth_attempts += 1
#
#                 # Если город достаточно большой (хотя бы 30% от цели)
#                 if current_size >= target_size * 0.3:
#                     # Размещаем город
#                     for x, y in city_cells:
#                         if (x, y) not in occupied:
#                             self.map[y, x] = 5
#                             occupied.add((x, y))
#
#                     self.cities.append({
#                         'center': (center_x, center_y),
#                         'size': current_size,
#                         'cells': list(city_cells)
#                     })
#                     print(
#                         f"🏙️ Город {city_num + 1}: {current_size} клеток (цель: {target_size}, форма: {len(city_cells)} клеток)")
#                     placed = True
#
#                 attempts += 1
#
#             if not placed:
#                 print(f"⚠️ Не удалось разместить город {city_num + 1}")
#
#         total_cells = np.sum(self.map == 5)
#         print(f"✅ Всего создано городов: {len(self.cities)}")
#         print(f"📊 Города занимают {total_cells} клеток")
#         return self.cities
#
#     def add_resources(self):
#         """Более разнообразные ресурсы"""
#         self.resources = np.zeros((self.height, self.width), dtype=int)
#
#         for y in range(self.height):
#             for x in range(self.width):
#                 terrain = self.map[y, x]
#                 moisture = self.moisture[y, x]
#
#                 # Железо в горах
#                 if terrain in [3, 11] and random.random() < 0.15:
#                     self.resources[y, x] = 1
#
#                 # Древесина в лесах
#                 elif terrain in [2, 10] and random.random() < 0.1:
#                     self.resources[y, x] = 2
#
#                 # Золото в горах (редко)
#                 elif terrain in [12] and random.random() < 0.05:
#                     self.resources[y, x] = 3
#
#                 # Нефть в болотах или степях
#                 elif terrain in [8, 9] and random.random() < 0.07:
#                     self.resources[y, x] = 4
#
#                 # Рыба в воде
#                 elif terrain in [0, 6] and random.random() < 0.08:
#                     self.resources[y, x] = 5
#
#         return self.resources
#
#     # ============ ОСНОВНОЙ КЛАСС КАРТЫ (УПРОЩЕННЫЙ) ============

