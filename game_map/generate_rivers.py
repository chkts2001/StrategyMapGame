import random
import math
from .map_data import MapData
import numpy as np
from typing import List, Tuple, Set


class RiverGenerator:
    def __init__(self, map_data):
        self.data = map_data
        self.river_cells = set()
        self.buffer_zones = set()
        self.min_angle = 145 * math.pi / 180  # 145 градусов в радианах

    def generate_rivers(self, num_rivers=5):
        """Главный метод генерации рек"""
        print(f"\n🌊 Генерация {num_rivers} рек...")

        rivers_created = 0
        for i in range(num_rivers):
            success = self._create_mountain_river() if i < num_rivers // 2 else self._create_edge_river()
            rivers_created += success
            print(f"   {'✅' if success else '⚠️'} Река {i + 1}")

        print(f"\n📊 Итого: {rivers_created}/{num_rivers}")
        return rivers_created

    def _create_mountain_river(self) -> bool:
        for _ in range(40):
            source = self._find_mountain_source()
            if source:
                river = self._grow_river(source[0], source[1], True)
                if len(river) >= 12:
                    self._save_river(river)
                    return True
        return False

    def _create_edge_river(self) -> bool:
        for _ in range(40):
            start = self._find_edge_start()
            if start:
                river = self._grow_river(start[0], start[1], False)
                if len(river) >= 12:
                    self._save_river(river)
                    return True
        return False

    def _grow_river(self, start_x: int, start_y: int, is_mountain: bool) -> List[Tuple[int, int]]:
        river = [(start_x, start_y)]
        x, y = float(start_x), float(start_y)

        # Начальный угол
        angle = self._get_start_angle(start_x, start_y, is_mountain)
        last_angle = angle
        straight_steps = 0

        for _ in range(300):
            # Каждый шаг - новый угол (никогда не идем прямо)
            # Поворачиваем на 25-35 градусов
            change = random.uniform(25, 35) * math.pi / 180
            change *= random.choice([-1, 1])  # случайная сторона
            angle += change

            # Нормализуем угол
            angle = self._normalize_angle(angle)

            # Проверяем угол поворота относительно прошлого направления
            angle_diff = abs(self._angle_difference(angle, last_angle))

            # Если поворот слишком большой (>35 градусов), корректируем
            if angle_diff > 35 * math.pi / 180:
                angle = last_angle + (25 * math.pi / 180) * (1 if angle > last_angle else -1)
                angle = self._normalize_angle(angle)

            last_angle = angle
            straight_steps = 0  # Никогда не идем прямо

            # Движение
            new_x = x + math.cos(angle) * 1.5
            new_y = y + math.sin(angle) * 1.5
            cell_x, cell_y = int(round(new_x)), int(round(new_y))

            # Пропускаем если не сдвинулись
            if (cell_x, cell_y) == river[-1]:
                continue

            # Проверка валидности
            if not self._can_place_cell(cell_x, cell_y, river, len(river) == 1):
                cell_x, cell_y = self._find_neighbor(cell_x, cell_y, river)
                if not cell_x:
                    break

            if (cell_x, cell_y) in river:
                break

            river.append((cell_x, cell_y))
            x, y = float(cell_x), float(cell_y)

            # Проверка на соединение с другой рекой
            if len(river) > 3 and (cell_x, cell_y) in self.river_cells:
                break

            if len(river) > 300:
                break

        # Пост-обработка для удаления острых углов
        return self._remove_sharp_angles(river)

    def _remove_sharp_angles(self, river: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Удаляет острые углы (менее 145 градусов)"""
        if len(river) < 3:
            return river

        smoothed = [river[0]]

        for i in range(1, len(river) - 1):
            prev = river[i - 1]
            curr = river[i]
            nxt = river[i + 1]

            # Вычисляем угол между направлениями
            v1 = (curr[0] - prev[0], curr[1] - prev[1])
            v2 = (nxt[0] - curr[0], nxt[1] - curr[1])

            angle = self._vector_angle(v1, v2)

            # Если угол острый (<145°), пропускаем точку
            if angle >= self.min_angle:
                smoothed.append(curr)

        smoothed.append(river[-1])
        return smoothed if len(smoothed) >= 3 else river

    def _vector_angle(self, v1: Tuple[int, int], v2: Tuple[int, int]) -> float:
        """Вычисляет угол между двумя векторами в радианах"""
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        norm1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
        norm2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

        if norm1 == 0 or norm2 == 0:
            return math.pi

        cos_angle = dot / (norm1 * norm2)
        cos_angle = max(-1, min(1, cos_angle))
        return math.acos(cos_angle)

    def _can_place_cell(self, x: int, y: int, river: List[Tuple[int, int]], is_start: bool) -> bool:
        if not self.data.is_valid_cell(x, y):
            return False

        # Горы (только старт)
        if not is_start and self.data.map[y][x] in [3, 7, 8, 10, 11, 12]:
            return False

        # Города
        if self.data.map[y][x] == 5:
            return False

        # Буферная зона (после 3 клеток)
        if len(river) > 3 and (x, y) in self.buffer_zones:
            return False

        return True

    def _find_neighbor(self, x: int, y: int, river: List[Tuple[int, int]]) -> Tuple[int, int]:
        for radius in range(1, 3):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    nx, ny = x + dx, y + dy
                    if self.data.is_valid_cell(nx, ny) and (nx, ny) not in river:
                        if self._can_place_cell(nx, ny, river, False):
                            return (nx, ny)
        return (None, None)

    def _get_start_angle(self, x: int, y: int, is_mountain: bool) -> float:
        if is_mountain and np.any(self.data.height_map):
            current_h = self.data.height_map[y, x]
            best_angle = math.pi / 2
            best_diff = 0

            for a in [0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi, -3 * math.pi / 4, -math.pi / 2,
                      -math.pi / 4]:
                dx, dy = int(round(math.cos(a))), int(round(math.sin(a)))
                nx, ny = x + dx, y + dy
                if self.data.is_valid_cell(nx, ny) and self.data.map[ny][nx] not in [3, 7, 8, 10, 11, 12, 5]:
                    diff = current_h - self.data.height_map[ny, nx]
                    if diff > best_diff:
                        best_diff = diff
                        best_angle = a

            if best_diff > 0:
                return best_angle

        # Начальный угол для края карты
        if x == 0:
            return random.uniform(-0.8, 0.8)
        if x == self.data.width - 1:
            return random.uniform(math.pi - 0.8, math.pi + 0.8)
        if y == 0:
            return random.uniform(0.3, math.pi - 0.3)
        if y == self.data.height - 1:
            return random.uniform(-math.pi + 0.3, -0.3)

        return random.uniform(0, 2 * math.pi)

    def _find_mountain_source(self) -> Tuple[int, int]:
        mountains = [3, 7, 8, 10, 11, 12]
        candidates = []

        for y in range(self.data.height):
            for x in range(self.data.width):
                if self.data.map[y][x] not in mountains:
                    continue

                if (x, y) in self.river_cells or (x, y) in self.buffer_zones:
                    continue

                # Проверяем выход
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = x + dx, y + dy
                    if self.data.is_valid_cell(nx, ny) and self.data.map[ny][nx] not in mountains + [5]:
                        candidates.append((x, y))
                        break

        return random.choice(candidates) if candidates else None

    def _find_edge_start(self) -> Tuple[int, int]:
        candidates = []

        for x in range(self.data.width):
            for y in [0, self.data.height - 1]:
                if self._is_valid_start(x, y):
                    candidates.append((x, y))

        for y in range(self.data.height):
            for x in [0, self.data.width - 1]:
                if self._is_valid_start(x, y):
                    candidates.append((x, y))

        return random.choice(list(set(candidates))) if candidates else None

    def _is_valid_start(self, x: int, y: int) -> bool:
        if (x, y) in self.river_cells or (x, y) in self.buffer_zones:
            return False
        if self.data.map[y][x] in [5, 3, 7, 8, 10, 11, 12]:
            return False
        return True

    def _normalize_angle(self, angle: float) -> float:
        """Нормализует угол в диапазон [-π, π]"""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def _angle_difference(self, a1: float, a2: float) -> float:
        """Вычисляет минимальную разницу между углами"""
        diff = abs(a1 - a2)
        return min(diff, 2 * math.pi - diff)

    def _save_river(self, river: List[Tuple[int, int]]):
        # Убираем дубликаты
        river = list(dict.fromkeys(river))

        # Сохраняем клетки
        for x, y in river:
            if self.data.map[y][x] != 5:
                self.data.map[y][x] = 4
                self.river_cells.add((x, y))

        # Буферная зона
        for x, y in river:
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    bx, by = x + dx, y + dy
                    if self.data.is_valid_cell(bx, by):
                        self.buffer_zones.add((bx, by))

    def clear(self):
        self.river_cells.clear()
        self.buffer_zones.clear()