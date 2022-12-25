import numpy as np
from queue import Queue

class Agent:
    def __init__(self, game_manager, initial_pos):
        self.game_manager = game_manager
        self.prob_map = np.zeros((game_manager.width, game_manager.height))
        self.cur_pos = initial_pos
        self.hints = Queue()

        return