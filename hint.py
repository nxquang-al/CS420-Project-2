import numpy as np

class HintManager:
    def __init__(self):
        return

    def generate(self):
        '''
        Return a random hint with its truth value
        Use switch-case here
        '''
        return 
    
    def gen_first_hint(self):
        '''
        generate the first hint, which is always true
        '''
        return
    
    def verify(self, data):
        return

    def gen_1st_type(self):
        '''
        A list of random tiles that doesn't contain the treasure (1 to 12)
        '''
        return  
    def gen_2nd_type(self):
        '''
        2-5 regions that 1 of them has the treasure.
        '''
        return  
    def gen_3rd_type(self):
        '''
        1-3 regions that do not contain the treasure.
        '''
        return 
    def gen_4th_type(self):
        '''
        A large rectangle area that has the treasure.
        '''
        return 
    def gen_5th_type(self):
        '''
        A small rectangle area that doesn't has the treasure.
        '''
        return 
    def gen_6th_type(self):
        '''
        He tells you that you are the nearest person to the treasure (between
        you and the prison he is staying).
        '''
        return 
    def gen_7th_type(self):
        '''
        A column and/or a row that contain the treasure (rare).
        '''
        return 
    def gen_8th_type(self):
        '''
        A column and/or a row that do not contain the treasure.
        '''
        return
    def gen_9th_type(self):
        '''
        2 regions that the treasure is somewhere in their boundary.
        '''
        return 
    def gen_10th_type(self):
        '''
        The treasure is somewhere in a boundary of 2 regions
        '''
        return 
    def gen_11th_type(self):
        '''
        The treasure is somewhere in an area bounded by 2-3 tiles from sea.
        '''
        return
    def gen_12th_type(self):
        '''
        A half of the map without treasure (rare).
        '''
        return 
    def gen_13th_type(self):
        '''
        From the center of the map/from the prison that he's staying, he tells
        you a direction that has the treasure (W, E, N, S or SE, SW, NE, NW)
        (The shape of area when the hints are either W, E, N or S is triangle).
        '''
        return 
    def gen_14th_type(self):
        '''
        2 squares that are different in size, the small one is placed inside the
        bigger one, the treasure is somewhere inside the gap between 2
        squares. (rare)
        '''
        return 
    def gen_15th_type(self):
        '''
        The treasure is in a region that has mountain.
        '''
        return 
    