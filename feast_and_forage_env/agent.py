import heapq

import numpy as np

from feast_and_forage_env.enums import Move, Tile


class Node:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f


class Agent:

    def __init__(self):
        self.available_moves = [Move.LEFT, Move.RIGHT, Move.UP, Move.DOWN]
        self.food_increase = 1
        self.passable_tiles = [Tile.GRASS, Tile.FOOD, Tile.SCRUB]

    @staticmethod
    def find_closest(pos, o, tile, passable_tiles):
        dists, _ = Agent.run_dikjstra(pos[0], pos[1], o, passable_tiles)
        # get all food distances
        ys, xs = np.where(o == tile)
        dists = [dists[y][x] for x, y in zip(xs, ys)]
        closest = np.argsort(dists)
        if len(closest) == 0:
            raise ResourceNotReachableException()
        # heading already to next food if distance==0, meaning player is on food already
        if dists[closest[0]] == 0:
            if len(closest) > 1:
                return ys[closest[1]], xs[closest[1]]
        return ys[closest[0]], xs[closest[0]]

    @staticmethod
    def run_dikjstra(y, x, map, passable_values):
        # meaning of the 100: init with a high positive distance instead -1 to indicate unreachable tiles
        dikjstra_map = np.full((len(map), len(map[0])), 100)
        visited_map = np.zeros((len(map), len(map[0])))
        queue = [(x, y, 0)]
        while len(queue) > 0:
            (cx, cy, cd) = queue.pop(0)
            cx, cy, cd = int(cx), int(cy), int(cd)
            if map[cy][cx] not in passable_values or (0 <= dikjstra_map[cy][cx] <= cd):
                continue
            visited_map[cy][cx] = 1
            dikjstra_map[cy][cx] = cd
            for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if nx < 0 or ny < 0 or nx >= len(map[0]) or ny >= len(map):
                    continue
                queue.append((nx, ny, cd + 1))
        return dikjstra_map, visited_map

    @staticmethod
    def heuristic(node, goal):
        # Manhattan distance heuristic
        return abs(node.x - goal.x) + abs(node.y - goal.y)

    def is_valid_move(self, grid, x, y):
        # Check if the move is within the grid and the cell is not blocked
        x, y = int(x), int(y)
        return 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] in self.passable_tiles

    def is_valid_move_water(self, grid, x, y):
        # Check if the move is within the grid and the cell is not blocked
        x, y = int(x), int(y)
        return 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] in (self.passable_tiles + [Tile.WATER])

    @staticmethod
    def astar(grid, start, goal, is_valid_move):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        open_list = []
        closed_set = set()

        start_node = Node(start[0], start[1])
        goal_node = Node(goal[0], goal[1])

        heapq.heappush(open_list, start_node)

        while open_list:
            current_node = heapq.heappop(open_list)
            closed_set.add((current_node.x, current_node.y))

            if current_node.x == goal_node.x and current_node.y == goal_node.y:
                path = []
                while current_node:
                    path.append((current_node.x, current_node.y))
                    current_node = current_node.parent
                return path[::-1]  # Reverse the path

            for dx, dy in directions:
                next_x, next_y = current_node.x + dx, current_node.y + dy

                if not is_valid_move(grid, next_x, next_y) or (next_x, next_y) in closed_set:
                    continue

                neighbor = Node(next_x, next_y, current_node)
                neighbor.g = current_node.g + 1
                neighbor.h = Agent.heuristic(neighbor, goal_node)
                neighbor.f = neighbor.g + neighbor.h

                heapq.heappush(open_list, neighbor)

        return []  # No path found

    @staticmethod
    def get_direction(pos1, pos2):
        diff = np.array(pos1) - np.array(pos2)
        if diff[0] == -1 and diff[1] == 0:
            return Move.DOWN
        elif diff[0] == 1 and diff[1] == 0:
            return Move.UP
        elif diff[0] == 0 and diff[1] == -1:
            return Move.RIGHT
        elif diff[0] == 0 and diff[1] == 1:
            return Move.LEFT
        elif diff[0] == 0 and diff[1] == 0:
            return Move.NOTHING  # "DONT MOVE"
        else:
            raise ValueError


class ResourceNotReachableException(Exception):
    def __init__(self):
        super().__init__("No food reachable.")
