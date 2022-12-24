from map import Map
from agent import Agent
from pirate import Pirate

class Game:
    def __init__(self):
        self.width = None
        self.height = None
        self.map = Map(self.width, self.height)
        self.agent = Agent(self, None)
        self.pirate = Pirate(None)
        return
    
    def log(self):
        '''
            Logging
        '''
        return
    
    def visualize(self):
        return