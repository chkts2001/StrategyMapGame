import matplotlib
matplotlib.use('TkAgg')  # Заставляет график открываться в отдельном окне

from game_map.game_map import GameMap
from config import *

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import json
from datetime import datetime


def setup_pycharm():
    """Настройка отображения для PyCharm"""
    # Включаем интерактивный режим matplotlib
    plt.ion()  # интерактивный режим
    # Настройка размера фигуры для окна PyCharm
    plt.rcParams['figure.figsize'] = [10, 8]
    plt.rcParams['figure.dpi'] = 100


def main():
    print("🚀 Запуск генератора карт...")

    # Настройка PyCharm
    setup_pycharm()

    # Создание карты
    game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)

    print("📊 Генерация ландшафта...")
    game_map.generate_perlin(scale=PERLIN_SCALE, octaves=PERLIN_OCTAVES)

    # game_map.generate_mountain_range(scale=40.0,
    #     octaves=6,
    #     center_x=100,
    #     center_y=100,
    #     size=80,              # радиус поиска места для массивов
    #     num_areas=3,          # КОЛИЧЕСТВО горных массивов (3 штуки)
    #     max_cells_per_area=100) # максимум клеток в одном массиве)  # 25% карты занято горами

    game_map.mountain_gen.generate_multiple_mountain_ranges(num_areas=3,
        size_per_area=50,
        peak_percent=0.20,      # 12% вершин
        mountain_percent=0.55,   # 45% гор
        hole_percent=0.15 )

    # river_count = np.sum(game_map.map == 4)
    # print(f"Количество клеток рек (тип 4): {river_count}")
    # print(f"Типы на карте: {np.unique(game_map.map)}")


    print("💧 Добавление рек...")
    game_map.generate_rivers(num_rivers=5)



    print("🏙️ Добавление городов...")
    game_map.city_gen.add_cities_random_shapes(num_cities=NUMBER_OF_CITIES, min_size=CITIES_MIN_SIZE, max_size=CITIES_MAX_SIZE)

    print("💎 Добавление ресурсов...")
    #game_map.add_resources()

    print("🎨 Визуализация карты...")
    visualize_map(game_map.data)

    print("💾 Сохранение карты...")
    save_map(game_map.data)

    print("✅ Готово!")

    # Оставляем окно открытым
    plt.ioff()
    plt.show()


def visualize_map(game_map):
    """Визуализация карты"""

    # Цвета для всех типов
    colors = [
        '#4d9eff',  # 0: вода - синий
        '#7CFC00',  # 1: равнина - зеленый
        '#228B22',  # 2: лес - темно-зеленый
        '#8B4513',  # 3: ГОРЫ - коричневый (темный)
        '#1E90FF',  # 4: река - голубой
        '#8b00ff',  # 5: город - золотой
        '#87CEEB',  # 6: мелководье - светло-голубой
        '#FFFFFF',  # 7: ВЕРШИНЫ - БЕЛЫЙ (снег)
        '#9ACD32',  # 8: холмы - светло-зеленый
        '#6B8E23',  # 9: лесистые холмы - желто-зеленый
        '#A0522D',  # 10: предгорья - светло-коричневый
        '#D2691E',  # 11: низкие горы - оранжево-коричневый
        '#5C4033'  # 12: скалы - темно-коричневый
    ]

    cmap = ListedColormap(colors)

    plt.figure(figsize=(12, 10))
    plt.imshow(game_map.map, cmap=cmap, interpolation='nearest', vmin=0, vmax=12)
    plt.title(f'Карта местности {game_map.width}x{game_map.height}')

    cbar = plt.colorbar(ticks=range(13))
    cbar.ax.set_yticklabels([
        '0: Вода',
        '1: Равнина',
        '2: Лес',
        '3: Горы',
        '4: Река',
        '5: Город',
        '6: Мелководье',
        '7: Вершины',
        '8: Холмы',
        '9: Лесистые холмы',
        '10: Предгорья',
        '11: Низкие горы',
        '12: Скалы'
    ])

    plt.show()

def save_map(game_map):
    """Сохранение карты в JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"maps/map_{timestamp}.json"

    data = {
        "width": game_map.width,
        "height": game_map.height,
        "tiles": game_map.map.tolist(),
        "cities": game_map.cities,
        "resources": game_map.resources.tolist()
    }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"📁 Карта сохранена: {filename}")


if __name__ == "__main__":
    main()