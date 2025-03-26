import os

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from feast_and_forage_env import config
from feast_and_forage_env.enums import PlayerID, Move, Tile
from feast_and_forage_env.level import Level
from feast_and_forage_env.player import Player


class Game:
    def __init__(self, level, player1, player2):
        self.initial_level = Level(level)
        self.current_level = Level(np.copy(level))
        self.turn = 0
        self.game_over = False
        self.winners = None

        # init
        pos_player1_y, pos_player1_x = np.where(self.current_level == Tile.PLAYER_1)
        pos_player2_y, pos_player2_x = np.where(self.current_level == Tile.PLAYER_2)

        self.players = {
            PlayerID.PLAYER_1: Player(PlayerID.PLAYER_1, pos_player1_x[0], pos_player1_y[0], player1),
            PlayerID.PLAYER_2: Player(PlayerID.PLAYER_2, pos_player2_x[0], pos_player2_y[0], player2)
        }

        self.current_level[self.players[PlayerID.PLAYER_1].y][self.players[PlayerID.PLAYER_1].x] = Tile.GRASS
        self.current_level[self.players[PlayerID.PLAYER_2].y][self.players[PlayerID.PLAYER_2].x] = Tile.GRASS

        self.moves = {Move.UP: self.move_up, Move.DOWN: self.move_down, Move.LEFT: self.move_left,
                      Move.RIGHT: self.move_right, Move.NOTHING: self.move_nothing}

    def plot_level(self, save=None):
        level = np.copy(self.current_level)
        level[self.players[PlayerID.PLAYER_1].y][self.players[PlayerID.PLAYER_1].x] = Tile.PLAYER_1
        level[self.players[PlayerID.PLAYER_2].y][self.players[PlayerID.PLAYER_2].x] = Tile.PLAYER_2

        images = {
            Tile.GRASS: np.array(Image.open(os.path.dirname(__file__) + "/assets/Grass.png").convert("RGB")),
            Tile.WATER: np.array(Image.open(os.path.dirname(__file__) + "/assets/Water.png").convert("RGB")),
            Tile.STONE: np.array(Image.open(os.path.dirname(__file__) + "/assets/Wall.png").convert("RGB")),
            Tile.FOOD: np.array(Image.open(os.path.dirname(__file__) + "/assets/Forest.png").convert("RGB")),
            Tile.PLAYER_1: np.array(Image.open(os.path.dirname(__file__) + "/assets/Player_Tile.png").convert("RGB")),
            Tile.PLAYER_2: np.array(Image.open(os.path.dirname(__file__) + "/assets/Opponent_Tile.png").convert("RGB")),
            Tile.SCRUB: np.array(Image.open(os.path.dirname(__file__) + "/assets/Forest_Used.png").convert("RGB"))
        }

        rows, cols = self.current_level.shape
        image_height, image_width, _ = images[0].shape
        composite_image = np.zeros((rows * image_height, cols * image_width, 3), dtype=np.uint8)

        for i in range(rows):
            for j in range(cols):
                composite_image[i * image_height:(i + 1) * image_height, j * image_width:(j + 1) * image_width] = \
                    images[level[i, j]]

        ax = plt.imshow(composite_image)
        plt.axis('off')  # Turn off axis
        plt.tight_layout()
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        if save is not None:
            plt.savefig(save, dpi=300)
        return ax

    def step(self, moves=None, verbose=False):
        if self.game_over is False:
            self.turn += 1

            if moves is None:
                moves = []
                for player_id, player in self.players.items():
                    moves.append({"player_id": player_id, "action": player.move(self.current_level)})

            for move in moves:
                self.moves[move["action"]](move["player_id"])
            self.tick_resources()
            self.check_tiles()

            winners = self.evaluate_win_cond()
            if winners is not None:
                self.game_over = True
                self.winners = winners
                if verbose is True:
                    print("GAME OVER, winners:", winners)

            if verbose is True:
                print("-" * 3, "ROUND", self.turn, "-" * 3)
                for player in self.players.values():
                    print(player)

            self.respawn_food()
            return None
        else:
            pass
        return {"total_steps": self.turn, "winners": self.evaluate_win_cond(),
                "players": {p_id: {"food": p.collected_food, "water": p.collected_water} for p_id, p in
                            self.players.items()}}

    def tick_resources(self):
        for p in self.players.values():
            if p.water > 0:
                p.water -= p.stats.water_drop
            if p.food > 0:
                p.food -= p.stats.food_drop

            if p.water == 0 or p.food == 0:
                p.health -= p.stats.health_drop
            if p.water >= 50 and p.food >= 50 and p.health < p.stats.max_health:
                p.health += p.stats.health_regain

    def check_tiles(self):
        # check for adjacent water tiles
        for player_id, player in self.players.items():
            if self.current_level.water_adjacent(player.x, player.y) is True:
                player.water = player.stats.max_water
                player.collected_water += 1

        # handle food tiles
        for player_id, player in self.players.items():
            if self.current_level[player.y][player.x] == Tile.FOOD:
                player.food = player.stats.max_food
                self.current_level[player.y][player.x] = Tile.SCRUB
                player.collected_food += player.agent.food_increase

                # if both players are on the same berry bush, set both health to 100
                if self.players[PlayerID.PLAYER_1].x == self.players[PlayerID.PLAYER_2].x and self.players[
                    PlayerID.PLAYER_1].y == self.players[PlayerID.PLAYER_2].y:
                    self.players[PlayerID.PLAYER_2].food = self.players[PlayerID.PLAYER_2].stats.max_food
                    self.players[PlayerID.PLAYER_2].collected_food += self.players[
                        PlayerID.PLAYER_2].agent.food_increase
                    break

    def evaluate_win_cond(self):
        winners = [p.player_id for p in self.players.values() if p.collected_food >= p.stats.collect_num_food]
        losers = [p.player_id for p in self.players.values() if p.health <= 0]
        # both lost --> draw
        if len(losers) == len(self.players.keys()):
            return losers
        # get the player ID of not loosing player
        if len(losers) == 1:
            return [p.player_id for p in self.players.values() if p.player_id != losers[0]]
        if len(winners) > 0:
            return winners

    def respawn_food(self):
        scrubs_y, scrubs_x = np.where(self.current_level == Tile.SCRUB)
        for y, x in zip(scrubs_y, scrubs_x):
            if np.random.random(1)[0] <= config.FOOD_RESPAWN:
                self.current_level[y][x] = Tile.FOOD

    def move_left(self, player_id):
        player = self.players[player_id]
        if self.players[player_id].agent.is_valid_move(self.current_level, player.y, player.x - 1):
            player.x -= 1

    def move_right(self, player_id):
        player = self.players[player_id]
        if self.players[player_id].agent.is_valid_move(self.current_level, player.y, player.x + 1):
            player.x += 1

    def move_up(self, player_id):
        player = self.players[player_id]
        if self.players[player_id].agent.is_valid_move(self.current_level, player.y - 1, player.x):
            player.y -= 1

    def move_down(self, player_id):
        player = self.players[player_id]
        if self.players[player_id].agent.is_valid_move(self.current_level, player.y + 1, player.x):
            player.y += 1

    def move_nothing(self, player_id):
        pass
