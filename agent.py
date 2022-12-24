import numpy as np

class Agent:
    def __init__(self, game_manager, initial_pos):
        self.prob_map = np.zeros((game_manager.width, game_manager.height))
        self.cur_pos = initial_pos
        return