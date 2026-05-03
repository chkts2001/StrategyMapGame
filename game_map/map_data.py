import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class MapData:
    width: int
    height: int
    map: np.ndarray = field(init=False)
    resources: np.ndarray = field(init=False)
    moisture: np.ndarray = field(init=False)
    height_map: np.ndarray = field(init=False)
    cities: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        """Инициализация массивов после создания"""
        self.map = np.zeros((self.height, self.width), dtype=int)
        self.resources = np.zeros((self.height, self.width), dtype=int)
        self.moisture = np.zeros((self.height, self.width))
        self.height_map = np.zeros((self.height, self.width))

    def get_terrain(self, x: int, y: int) -> int:
        """Безопасное получение типа местности"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.map[y, x]
        return -1

    def set_terrain(self, x: int, y: int, value: int):
        """Безопасная установка типа местности"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.map[y, x] = value

    def is_valid_cell(self, x: int, y: int) -> bool:
        """Проверка, находится ли клетка в границах карты"""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell_info(self, x: int, y: int) -> dict:
        """Получение всей информации о клетке"""
        if not self.is_valid_cell(x, y):
            return {}
        return {
            'terrain': self.map[y, x],
            'height': self.height_map[y, x],
            'moisture': self.moisture[y, x],
            'resource': self.resources[y, x]
        }