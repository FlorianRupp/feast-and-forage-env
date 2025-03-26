import numpy as np

from feast_and_forage_env.agent import Agent, ResourceNotReachableException
from feast_and_forage_env.enums import Tile, Move


class RandomAgent(Agent):
    def __call__(self, *args, **kwargs):
        return np.random.choice(self.available_moves)


class ForageAgent(Agent):
    def __call__(self, level, x, y):
        pos = (y, x)
        try:
            closest_food = self.find_closest(pos, level, Tile.FOOD, self.passable_tiles)
            path = Agent.astar(level, pos, closest_food, self.is_valid_move)
            if len(path) >= 2:
                return Agent.get_direction(path[0], path[1])
            else:
                raise ResourceNotReachableException()

        except ResourceNotReachableException:
            # if no food reachable head to nearest water
            try:
                closest_water = self.find_closest(pos, level, Tile.WATER, self.passable_tiles + [Tile.WATER])
                path = Agent.astar(level, pos, closest_water, self.is_valid_move_water)
                if len(path) >= 2:
                    return Agent.get_direction(path[0], path[1])
            except ResourceNotReachableException:
                pass
            return Move.NOTHING


class HandicapAgent(ForageAgent):
    def __init__(self):
        super().__init__()
        self.moved = False

    def __call__(self, level, x, y):
        if self.moved is False:
            self.moved = True
            return super().__call__(level, x, y)
        else:
            self.moved = False
            return Move.NOTHING


class DoubleFoodAgent(ForageAgent):
    # always collects 2 from one food resource
    def __init__(self):
        super().__init__()
        self.food_increase = 2


class MountainMoveAgent(ForageAgent):
    # can walk over stones
    def __init__(self):
        super().__init__()
        self.passable_tiles = [Tile.GRASS, Tile.FOOD, Tile.SCRUB, Tile.STONE]
