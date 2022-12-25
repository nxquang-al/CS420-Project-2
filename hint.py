import numpy as np

class HintManager:
    def __init__(self, data):
        self.data = data
        self.agent_pos = None
        self.pirate_pos = None
        return

    def generate(self, agent_pos, pirate_pos):
        '''
        Return a random hint with its truth value
        Use switch-case here
        '''
        #need to update to get the latest positions of the agent and pirate so we can generate the 6th typed hint
        self.agent_pos = agent_pos
        self.pirate_pos = pirate_pos
        
        hint_type = np.random.randint(1, 16)
        
        if (hint_type == 1):
            hint = self.gen_1st_type()
        elif (hint_type == 2): 
            hint = self.gen_2nd_type()
        elif (hint_type == 3):
            hint = self.gen_3rd_type()
        elif (hint_type == 4): 
            hint = self.gen_4th_type()
        elif (hint_type == 5): 
            hint = self.gen_5th_type()
        elif (hint_type == 6): 
            hint = self.gen_6th_type()
        elif (hint_type == 7): 
            hint = self.gen_7th_type()
        elif (hint_type == 8): 
            hint = self.gen_8th_type()
        elif (hint_type == 9): 
            hint = self.gen_9th_type()
        elif (hint_type == 10): 
            hint = self.gen_10th_type()
        elif (hint_type == 11): 
            hint = self.gen_11th_type()
        elif (hint_type == 12): 
            hint = self.gen_12th_type()
        elif (hint_type == 13): 
            hint = self.gen_13th_type()
        elif (hint_type == 14): 
            hint = self.gen_14th_type()
        else: 
            hint = self.gen_15th_type()

        return hint
    
    def gen_first_hint(self, agent_pos, pirate_pos):
        '''
        generate the first hint, which is always true
        '''
        self.agent_pos = agent_pos
        self.pirate_pos = pirate_pos
        
        hint_type = np.random.randint(1, 16)
        truth_val = False

        while truth_val == False:        
            if (hint_type == 1):
                hint = self.gen_1st_type()
            elif (hint_type == 2): 
                hint = self.gen_2nd_type()
            elif (hint_type == 3):
                hint = self.gen_3rd_type()
            elif (hint_type == 4): 
                hint = self.gen_4th_type()
            elif (hint_type == 5): 
                hint = self.gen_5th_type()
            elif (hint_type == 6): 
                hint = self.gen_6th_type()
            elif (hint_type == 7): 
                hint = self.gen_7th_type()
            elif (hint_type == 8): 
                hint = self.gen_8th_type()
            elif (hint_type == 9): 
                hint = self.gen_9th_type()
            elif (hint_type == 10): 
                hint = self.gen_10th_type()
            elif (hint_type == 11): 
                hint = self.gen_11th_type()
            elif (hint_type == 12): 
                hint = self.gen_12th_type()
            elif (hint_type == 13): 
                hint = self.gen_13th_type()
            elif (hint_type == 14): 
                hint = self.gen_14th_type()
            else: 
                hint = self.gen_15th_type()

            truth_val = hint[1]

        return hint
    
    def verify(self, data):

        return

    def gen_1st_type(self):
        '''
        A list of random tiles that doesn't contain the treasure (1 to 12)
        '''
        #random the number of random tiles 1 - 12
        num_tiles = np.random.randint(1, 13)
        
        truth_val = True
        
        #create an numpy array of num_tiles tuples (0, 0)
        # example: [(-1,-1),(-1,-1),(-1,-1),...] 
        list_tiles = np.full(num_tiles, (-1, -1), (np.int64, (2,)))

        width, height = self.data.width, self.data.height
        
        for i in range(num_tiles):
            while True:
                col = np.random.randint(width)
                row = np.random.randint(height)
                if (col, row) not in list_tiles: #random until we get a tile that has not been selected
                    break

            list_tiles[i] = (col, row)           #do this instead of append because it is faster      
            
        if self.data.treasure in list_tiles:
            truth_val = False

        return 1, truth_val, list_tiles

    def gen_2nd_type(self):
        '''
        2-5 regions that 1 of them has the treasure.
        '''
        #random the number of regions from 2-5
        num_regions = np.random.randint(2, 6)
        
        truth_val = True

        #choose randomly num_regions regions 
        list_regions = np.random.choice(np.arange(1, self.data.num_regions), (num_regions,), replace=False)

        if self.data.map[self.data.treasure] not in list_regions:
            truth_val = False

        list_tiles = None
        for region in list_regions:      
            if list_tiles is None:
                list_tiles = np.asarray(np.where(self.data.map == region)).T
            else:
                list_tiles = np.concatenate((list_tiles, np.asarray(np.where(self.data.map == region)).T), axis=0)
        
        print(list_regions)
        return 2, truth_val, list_tiles  
    
    def gen_3rd_type(self):
        '''
        1-3 regions that do not contain the treasure.
        '''
        num_regions = np.random.randint(1, 4)
        
        truth_val = True

        list_regions = np.random.choice(np.arange(1, self.data.num_regions), (num_regions,), replace=False)

        if self.data.map[self.data.treasure] in list_regions:
            truth_val = False

        list_tiles = None
        for region in list_regions:      
            if list_tiles is None:
                list_tiles = np.asarray(np.where(self.data.map == region)).T
            else:
                list_tiles = np.concatenate((list_tiles, np.asarray(np.where(self.data.map == region)).T), axis=0)
        
        print(list_regions)
        return 3, truth_val, list_tiles 
 
    def gen_4th_type(self):
        '''
        A large rectangle area that has the treasure.
        '''
        map_area = self.data.width * self.data.height
        selected_area = 0
        truth_val = True

        while True:
            col = np.sort(np.random.choice(np.arange(self.data.width), (2,), replace=False)) #choose 2 coordinates x from 0 - width and sort ascending
            row = np.flip(np.sort(np.random.choice(np.arange(self.data.height), (2,), replace=False))) #choose 2 coordinates y from 0 - height and sort descending
            
            selected_area = (col[1] - col[0]) * (row[0] - row[1]) 
            
            if selected_area >= 0.3 * map_area and selected_area < 0.6 * map_area: #large rectangle area is an area that must be as big as 30% - 60% total area of the map
                rectangle = np.concatenate((col, row), axis=0) #this array has 4 elements representing for rectangle's coordinates [top_left_x, bottom_right_x, top_left_y, bottom_right_y]
                break
        
        #if the treasure is outside the rectangle, this hint is false
        if self.data.treasure[0] < rectangle[0] or self.data.treasure[0] > rectangle[1] or self.data.treasure[1] > rectangle[2] or self.data.treasure[1] < rectangle[3]:
            truth_val = False

        #get the list of coordinates of titles which are inside the rectangle
        list_tiles = np.stack(
                        np.meshgrid(
                            [col for col in range(rectangle[0], rectangle[1] + 1)], 
                            [row for row in range(rectangle[3], rectangle[2] + 1)]
                        ), 
                        -1
                    ).reshape(-1, 2) 
        
        print(rectangle)
        return 4, truth_val, list_tiles

    def gen_5th_type(self):
        '''
        A small rectangle area that doesn't has the treasure.
        '''
        map_area = self.data.width * self.data.height
        selected_area = 0
        truth_val = True

        while True:
            col = np.sort(np.random.choice(np.arange(self.data.width), (2,), replace=False)) #choose 2 coordinates x from 0 - width and sort ascending
            row = np.flip(np.sort(np.random.choice(np.arange(self.data.height), (2,), replace=False))) #choose 2 coordinates y from 0 - height and sort descending
            
            selected_area = (col[1] - col[0]) * (row[0] - row[1]) 
            
            if selected_area >= 0.1 * map_area and selected_area < 0.3 * map_area: #small rectangle area is an area that must be as big as 10% - 30% total area of the map
                rectangle = np.concatenate((col, row), axis=0) #this array has 4 elements representing for rectangle's coordinates [top_left_x, bottom_right_x, top_left_y, bottom_right_y]
                break
        
        #if the treasure is outside the rectangle, this hint is false
        if not (self.data.treasure[0] < rectangle[0] or self.data.treasure[0] > rectangle[1] or self.data.treasure[1] > rectangle[2] or self.data.treasure[1] < rectangle[3]):
            truth_val = False

        #get the list of coordinates of titles which are inside the rectangle
        list_tiles = np.stack(
                        np.meshgrid(
                            [col for col in range(rectangle[0], rectangle[1] + 1)], 
                            [row for row in range(rectangle[3], rectangle[2] + 1)]
                        ), 
                        -1
                    ).reshape(-1, 2) 
        
        print(rectangle)
        return 5, truth_val, list_tiles 

    def gen_6th_type(self):
        '''
        He tells you that you are the nearest person to the treasure (between
        you and the prison he is staying).
        '''
        truth_val = True
        
        agent_distance = sum(abs(self.agent_pos[0] - self.data.treasure[0]), abs(self.agent_pos[1] - self.data.treasure[1]))
        pirate_distance = sum(abs(self.pirate_pos[0] - self.data.treasure[0]), abs(self.pirate_pos[1] - self.data.treasure[1]))
        
        if (agent_distance > pirate_distance):
            truth_val = False

        return 6, truth_val
        
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
    