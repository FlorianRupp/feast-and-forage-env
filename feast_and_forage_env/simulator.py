import numpy as np

from feast_and_forage_env.game import Game


class Simulator:

    def __init__(self, level, player1, player2):
        self.level = level
        self.player1 = player1
        self.player2 = player2

    def run(self, n, return_balancing=True, round_=False):
        winners = []
        for i in range(n):
            game = Game(self.level, self.player1, self.player2)
            while game.game_over is False:
                game.step()
            winners.extend(game.winners)
        if return_balancing is False:
            return winners
        else:
            if round_ is True:
                return round(np.mean(winners), 1)
            return np.mean(winners)
