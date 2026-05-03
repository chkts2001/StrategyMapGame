import random
import math
from .map_data import MapData
import numpy as np

class CityGenerator:
    def __init__(self, map_data: MapData):
        self.data = map_data

    def add_cities_random_shapes(self, num_cities=10, min_size=1, max_size=40):
        """Генерация городов случайных форм от 1 до 40 клеток"""

        self.data.cities = []
        occupied = set()  # Запоминаем занятые клетки

        for city_num in range(num_cities):
            target_size = random.randint(min_size, max_size)

            # Ищем подходящий центр
            attempts = 0
            placed = False

            while not placed and attempts < 200:
                # Случайный центр
                center_x = random.randint(5, self.data.width - 5)
                center_y = random.randint(5, self.data.height - 5)

                # Центр не должен быть на воде, горах или реке
                if self.data.map[center_y, center_x] in [0, 3, 4, 6]:
                    attempts += 1
                    continue

                # Создаем случайную форму
                city_cells = set()
                city_cells.add((center_x, center_y))

                # Алгоритм случайного роста (как снежинка)
                current_size = 1
                growth_attempts = 0

                while current_size < target_size and growth_attempts < target_size * 5:
                    # Выбираем случайную клетку из уже добавленных
                    if not city_cells:
                        break

                    source_cell = random.choice(list(city_cells))
                    sx, sy = source_cell

                    # Случайное направление для новой клетки
                    dx = random.choice([-1, 0, 1])
                    dy = random.choice([-1, 0, 1])

                    # Пропускаем нулевое направление (оставаться на месте)
                    if dx == 0 and dy == 0:
                        growth_attempts += 1
                        continue

                    new_x = sx + dx
                    new_y = sy + dy

                    # Проверяем границы
                    if not self.data.is_valid_cell(new_x, new_y):
                        growth_attempts += 1
                        continue

                    # Проверяем, не занято ли
                    if (new_x, new_y) in occupied:
                        growth_attempts += 1
                        continue

                    # Проверяем, подходит ли местность
                    if self.data.map[new_y, new_x] in [0, 3, 4, 6]:  # вода, горы, реки
                        growth_attempts += 1
                        continue

                    # Добавляем новую клетку
                    if (new_x, new_y) not in city_cells:
                        city_cells.add((new_x, new_y))
                        current_size += 1
                        growth_attempts = 0
                    else:
                        growth_attempts += 1

                # Если город достаточно большой (хотя бы 30% от цели)
                if current_size >= target_size * 0.3:
                    # Размещаем город
                    for x, y in city_cells:
                        if (x, y) not in occupied:
                            self.data.map[y, x] = 5
                            occupied.add((x, y))

                    self.data.cities.append({
                        'center': (center_x, center_y),
                        'size': current_size,
                        'cells': list(city_cells)
                    })
                    print(
                        f"🏙️ Город {city_num + 1}: {current_size} клеток (цель: {target_size}, форма: {len(city_cells)} клеток)")
                    placed = True

                attempts += 1

            if not placed:
                print(f"⚠️ Не удалось разместить город {city_num + 1}")

        total_cells = np.sum(self.data.map == 5)
        print(f"✅ Всего создано городов: {len(self.data.cities)}")
        print(f"📊 Города занимают {total_cells} клеток")
        return self.data.cities