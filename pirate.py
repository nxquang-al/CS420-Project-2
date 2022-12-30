import numpy as np
from queue import Queue
from hint import HintManager

class Pirate:
    '''
        This class manage the behavior of pirate
    '''
    def __init__(self, inital_pos):
        self.path = None # A queue of cells, which is the shortest path to treasure
        self.visited = None # A numpy array of visited cells
    
    def find_shortest_path(self):
        '''
            Find shortes path to treasure using A* search
        '''
        return

