from map import Map
from agent import Agent
from pirate import Pirate
from hint import HintManager
import random
import numpy as np

class Game:
    def __init__(self):
        self.WIDTH = None
        self.HEIGHT = None
        self.map_manager = Map(self.WIDTH, self.HEIGHT)
        self.hint_manager = HintManager(self.map_manager)
        self.truth_list = []
        self.pirate = Pirate(None)

        agent_pos = (random.randint(0,self.WIDTH-1), random.randint(0, self.HEIGHT-1))
        self.agent = Agent(self, agent_pos)
        
        self.prison_revealTurn = random.randint(2,4)
        self.pirate_freeTurn = int(4+0.2*self.WIDTH)   # To ensure prirate is free after prison's position is revealed


        self.logs = []
        self.logs.append('Game start')
        self.logs.append('Agent appears at {}}'.format(self.agent_pos))
        self.logs.append('The pirate\'s will be revealed at the beginning of turn {}'.format(self.prison_reveal_turn))
        self.logs.append('The pirate will be free at the beginning of turn {}'.format(self.pirate_free_turn))
    

    def is_movable(self, pos):
        return self.map_manager.is_movable(pos)

    def scan_rectangle(self,top_left, bot_right):
        return self.map_manager.check_rectangle_region(top_left, bot_right)

    def log(self):
        '''
            Logging
        '''
        return
    
    def visualize(self):
        return

    def generate_turn(self, turn_idx):
        self.logs.append('START TURN {}'.format(turn_idx))
        if turn_idx == 1:
            hint_type, log, truth, data = self.hint_manager.gen_first_hint()
        else:
            hint_type, log, truth, data = self.hint_manager.generate()
        self.truth_list.append(truth)
        self.agent.add_hint(turn_idx, hint_type, data)

        self.logs.append('HINT {}: {}'.format(turn_idx, log))
        self.logs.append('ADD HINT {turn_idx} TO HINT LIST')
        if turn_idx == 1:
            self.logs.append('HINT 1: is_verified = TRUE, is_truth = TRUE')
    
    def get_hint_truth(self, hint_idx):
        return self.truth_list[hint_idx]

    def get_region_tiles(self, region_idices) -> np.ndarray:
        '''
        Give a list of region, get the binary map of these regions' tiles
        '''
        return np.isin(self.map_manager.map, region_idices)

    def get_all_boundaries(self):
        '''
        Find all tiles which are boundary, except sea
        '''
        return self.map_manager.get_all_boundaries()
    
    def get_two_regions_boundary(self, rid_1, rid_2):
        '''
        Give 2 region indices, return their border tiles
        '''
        return self.map_manager.get_two_regions_boundary(rid_1, rid_2)


    def run(self):
        self.turn_idx = 1
        self.can_tele = False
        self.pirate_isFree = False

        while True:
            self.logs.appen('START TURN {}'.format(self.turn_idx))

            if self.turn_idx == self.prison_revealTurn:
                self.logs.append("The location of pirate is {}".format())


