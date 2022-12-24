import numpy as np

class Map:
    '''
        This class will manage everything related to map
    '''
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = np.zeros((width, height))
        self.num_mountains = None
        self.num_prisons = None
        self.mountains = None # numpy array of tuples [(x0,y0), (x1,y1),...]
        self.prisons = None # numpy array of tuples
    
    def generate_map(self):
        return
    
    def isMovable(self,x,y):
        '''
            Check if this cell is moveable (not mountain, sea)
        '''
        return
    
    def get_regions__of_mountains(self):
        '''
            For hint 14th
        '''
        return
    
