import numpy as np
import random

class HintManager:
    def __init__(self, map):
        self.map = map
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
        
        #create an numpy array of num_tiles arrays [0, 0]
        # example: [[-1,-1],[-1,-1],[-1,-1],...] 
        array_of_tiles = np.full(num_tiles, [-1, -1], (np.int64, (2,)))
        
        for i in range(num_tiles):
            while True:
                col = np.random.randint(self.map.width)
                row = np.random.randint(self.map.height)
                if [col, row] not in array_of_tiles: #random until we get a tile that has not been selected
                    break

            array_of_tiles[i] = (col, row)           #do this instead of append because it is faster      

        log = "A list of tiles [{}] doesn't contain the treasure".format(self.map.convert_to_string(array_of_tiles))

        truth = True
        if self.map.treasure_pos in array_of_tiles:
            truth = False

        return 1, log, truth, array_of_tiles

    def gen_2nd_type(self):
        '''
        2-5 regions that 1 of them has the treasure.
        '''
        num_regions = np.random.randint(2, 6)

        list_regions = np.random.choice(np.arange(1, self.map.num_regions), (num_regions,), replace=False)

        log = "One of the regions {} has the treasure".format(self.map.convert_to_string(list_regions))
        
        truth, array_of_tiles = self.map.check_region(list_regions)
        
        return 2, log, truth, list_regions

    def gen_3rd_type(self):
        '''
        1-3 regions that do not contain the treasure.
        '''
        num_regions = np.random.randint(1, 4)

        list_regions = np.random.choice(np.arange(1, self.map.num_regions), (num_regions,), replace=False)

        log = "Regions {} do not contain the treasure".format(self.map.convert_to_string(list_regions))
        
        truth, array_of_tiles = self.map.check_region(list_regions)
        
        return 3, log, not truth, list_regions

    def gen_4th_type(self):
        '''
        A large rectangle area that has the treasure.
        '''
        map_area = self.map.width * self.map.height
        rectangle = None

        while True:
            col = np.sort(np.random.choice(np.arange(self.map.width), (2,), replace=False)) #choose 2 coordinates x from 0 - width and sort ascending
            row = np.flip(np.sort(np.random.choice(np.arange(self.map.height), (2,), replace=False))) #choose 2 coordinates y from 0 - height and sort descending
            
            selected_area = (col[1] - col[0]) * (row[0] - row[1]) 
            
            if selected_area >= 0.3 * map_area and selected_area < 0.6 * map_area: #large rectangle area is an area that must be as big as 30% - 60% total area of the map
                rectangle = np.array([col[0], row[0], col[1], row[1]]) #this array has 4 elements representing for rectangle's coordinates [top_left_x, bottom_right_x, top_left_y, bottom_right_y]
                break
        
        log = "A large rectangle area has the treasure. Top-Left-Bottom-Right = [{}]".format(self.map.convert_to_string(rectangle))

        truth, array_of_tiles = self.map.check_rectangle(rectangle)
        
        return 4, log, truth, array_of_tiles

    def gen_5th_type(self):
        '''
        A small rectangle area that doesn't has the treasure.
        '''
        map_area = self.map.width * self.map.height
        rectangle = None

        while True:
            col = np.sort(np.random.choice(np.arange(self.map.width), (2,), replace=False)) #choose 2 coordinates x from 0 - width and sort ascending
            row = np.flip(np.sort(np.random.choice(np.arange(self.map.height), (2,), replace=False))) #choose 2 coordinates y from 0 - height and sort descending
            
            selected_area = (col[1] - col[0]) * (row[0] - row[1]) 
            
            if selected_area >= 0.1 * map_area and selected_area < 0.3 * map_area: #large rectangle area is an area that must be as big as 30% - 60% total area of the map
                rectangle = np.array([col[0], row[0], col[1], row[1]]) #this array has 4 elements representing for rectangle's coordinates [top_left_x, bottom_right_x, top_left_y, bottom_right_y]
                break
        
        log = "A small rectangle area doesn't has the treasure. Top-Left-Bottom-Right = [{}]".format(self.map.convert_to_string(rectangle))

        truth, array_of_tiles = self.map.check_rectangle(rectangle)
        
        return 5, log, not truth, array_of_tiles

    def gen_6th_type(self):
        '''
        He tells you that you are the nearest person to the treasure (between
        you and the prison he is staying).
        '''
        log = "You are the nearest person to the treasure"
        
        truth = self.map.check_distance(self.agent_pos, self.pirate_pos)
        
        return 6, log, truth
        
    def gen_7th_type(self):
        '''
        A column and/or a row that contain the treasure (rare).
        '''
        width, height = self.map.get_map_shape()
        choice = random.choice([0,1,2], p=[0.45,0.45,0.1], size=1)[0]
        col, row = None, None
        log = ''
        truth = False
        if choice == 0:
            # Column
            col = random.randint(0,width)
            truth = self.map.check_column(col)
            log = 'Column {} contains the treasure'.format(col)
        elif choice ==1:
            # Row
            row = random.randint(0, height)
            truth = self.map.check_row(row)
            log = 'Row {} contains the treasure'.format(row)
        elif choice == 2:
            # Both
            col = random.randint(0,width)
            row = random.randint(0, height)
            truth = self.map.check_column(col) and self.map.check_row(row)
            log = 'Column {} and row {} contain the treasure'.format(col, row)       
        return 7, truth, log, (col, row)

    def gen_8th_type(self):
        '''
        A column and/or a row that do not contain the treasure.
        '''
        width, height = self.map.get_map_shape()
        choice = random.choice([0,1,2], p=[0.45,0.45,0.1], size=1)[0]
        col = row = None
        truth = False
        if choice == 0:
            # Column
            c = random.randint(0,width)
            column = np.expand_dims(np.arange(0,height), axis=1)
            column = np.pad(column, (1,0), 'constant', constant_values=c)
            truth = not self.map.check_column(c)
        elif choice ==1:
            # Row
            r = random.randint(0, height)
            row = np.expand_dims(np.arange(0,width), axis=1)
            row = np.pad(row, (0,1), 'constant', constant_values=r)
            truth = not self.map.check_row(r)
        elif choice == 2:
            # Both
            c = random.randint(0,width)
            column = np.expand_dims(np.arange(0,height), axis=1)
            column = np.pad(column, (1,0), 'constant', constant_values=c)
            r = random.randint(0, height)
            row = np.expand_dims(np.arange(0,width), axis=1)
            row = np.pad(row, (0,1), 'constant', constant_values=r)
            truth = not self.map.check_column(c) and not self.map.check_row(r)
        return 8, truth, np.concatenate((column, row), axis=0)

    def gen_9th_type(self):
        '''
        2 regions that the treasure is somewhere in their boundary.
        '''

        return 
    def gen_10th_type(self):
        '''
        The treasure is somewhere in a boundary of 2 regions
        '''
        truth = self.map.check_on_boundary()
        log = 'The treasure is somewhere in a boundary of 2 regions'
        return 10, truth, log
        
    def gen_11th_type(self):
        '''
        The treasure is somewhere in an area bounded by 2-3 tiles from sea.
        '''
        return
    def gen_12th_type(self):
        '''
        A half of the map without treasure (rare).
        '''
        width, height = self.map.get_map_shape()
        choice = random.randint(0,3) # 0: left, 1: right, 2: top, 3: right
        if choice == 0:     #left half
            top_left = (0,0)
            bot_right = (width // 2, height)
        elif choice == 1:   #right half
            top_left = (width // 2, 0)
            bot_right = (width, height)
        elif choice == 3:   #top half
            top_left = (0,0)
            bot_right = (width, height // 2)
        else:               #bottom half
            top_left = (0, height // 2)
            bot_right = (width, height)
        
        truth = self.map.check_rectangle_region(top_left, bot_right)
        return 12, truth, np.array([top_left, bot_right])

    def gen_13th_type(self, prison_pos):
        '''
        From the center of the map/from the prison that he's staying, he tells
        you a direction that has the treasure (W, E, N, S or SE, SW, NE, NW)
        (The shape of area when the hints are either W, E, N or S is triangle).
        '''
        choice = random.randint(0,7)
        if choice == 0:
            # East
            truth = self.map.check_direction(prison_pos, direction='E')
        elif choice == 1:
            # West
            truth = self.map.check_direction(prison_pos, direction='W')
        elif choice == 2:
            # North
            truth = self.map.check_direction(prison_pos, direction='N')
        elif choice == 3:
            # South
            truth = self.map.check_direction(prison_pos, direction='S')
        elif choice == 4:
            # South-East
            truth = self.map.check_direction(prison_pos, direction='SE')
        elif choice == 5:
            # South-West
            truth = self.map.check_direction(prison_pos, direction='SW')
        elif choice == 6:
            # North-East
            truth = self.map.check_direction(prison_pos, direction='NE')
        elif choice == 7:
            # North-West
            truth = self.map.check_direction(prison_pos, direction='NW')
        return 
 
    def gen_14th_type(self):
        '''
        2 squares that are different in size, the small one is placed inside the
        bigger one, the treasure is somewhere inside the gap between 2
        squares. (rare)
        '''
        map_area = self.map.width * self.map.height
        big_square = None
        small_square = None

        while True:
            #choose 2 top_left and bottom_left y coordinates for each square from 0 - width and sort ascendingly
            #the higgest and lowest y is belong to the the bigger square and the 2 left is smaller one's
            col = np.sort(np.random.choice(np.arange(self.map.width), (4,)))

            #choose 2 top_left and bottom_left x coordinates for each square from 0 - height and sort descendingly
            #the higgest and lowest x is belong to the the bigger square and the 2 left is smaller one's
            row = np.flip(np.sort(np.random.choice(np.arange(self.map.height), (4,))))
            
            small_area = (col[2] - col[1]) * (row[1] - row[2])

            #small square's area must be as big as 10% - 30% total area of the map
            if small_area >= 0.1 * map_area and small_area < 0.3 * map_area: 
                big_square = np.array([col[0], row[0], col[3], row[3]], dtype=np.int64)
                small_square = np.array([col[1], row[1], col[2], row[2]], dtype=np.int64)
                break

        log = "The treasure is somewhere in the gap between 2 squares: S1 = [{}], S2 = [{}]".format(self.map.convert_to_string(big_square), self.map.convert_to_string(small_square))
    
        truth, array_of_tiles = self.map.check_square_gap(big_square, small_square)

        return 14, log, truth, big_square, small_square
    
    def gen_15th_type(self):
        '''
        The treasure is in a region that has mountain.
        '''
        list_mountain_region = self.map.get_mountain_region()
        log = "The treasure is in one of the regions {} which have mountain".format(list_mountain_region)
        truth, array_of_tiles = self.map.check_region(list_mountain_region)
        return 15, log, truth, list_mountain_region
    