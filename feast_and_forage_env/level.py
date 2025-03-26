import numpy as np

from feast_and_forage_env.enums import Tile


class Level(np.ndarray):
    # overwriting the getitem function to return None for idx -1 or > shape
    def __new__(cls, input_array):
        obj = np.asarray(input_array).view(cls)
        return obj

    def __getitem__(self, item):
        if isinstance(item, int):
            if item < 0:
                return None
        try:
            return super().__getitem__(item)
        except IndexError:
            return None

    def water_adjacent(self, x, y):
        try:
            if self[y][x+1] == Tile.WATER:
                return True
        except TypeError:
            pass
        try:
            if self[y][x-1] == Tile.WATER:
                return True
        except TypeError:
            pass
        try:
            if self[y+1][x] == Tile.WATER:
                return True
        except TypeError:
            pass
        try:
            if self[y-1][x] == Tile.WATER:
                return True
        except TypeError:
            pass
        return False

