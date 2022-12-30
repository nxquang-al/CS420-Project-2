import numpy as np
from scipy.ndimage.morphology import binary_dilation

class Map:
    '''
        This class will manage everything related to map
    '''
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = np.zeros((width, height))
        self.__treasure_pos = None

        self.num_mountain = None
        self.mountains = []                         # Numpy array of mountaine array([m1, m2,...])
        self.num_prisons = None
        self.prisons =  None                        # Numpy array of prisons array([p1, p2, p3,...])

        self.num_regions = None
        self.adjacent_list = self.get_neighbors()    # List of numpy array of adjacent regions
    
    def get_map_shape(self):
        return (self.width, self.height)
    
    def generate_map(self):
        return
    
    def get_region_tiles(self, region_idx):
        return np.where(self.map==region_idx, 1, 0)
    
    def is_mountain(self, pos):
        pos = np.asarray(pos)
        return any(np.array_equal(pos, mountain) for mountain in self.mountains)

    def is_sea(self, pos):
        return self.map[pos] == 0

    def get_neighbors(self):
        '''
        This function finds adjacent regions of each region
        Return: list of N items, N is the number of regions
                Each item is a ndarray of indexes of adjacent regions
                [array([r1, r2]), array[r3, r4],...]

        '''
        num_regions = self.map.max()
        temp = np.zeros((num_regions+1, num_regions+1), dtype=bool)

        # Check vertical adjacency
        a, b = self.map[:-1, :], self.map[1:,:]
        temp[a[a!=b], b[a!=b]] = True

        # Check horizontal adjacency
        a, b = self.map[:, :-1], self.map[:, 1:]
        temp[a[a!=b], b[a!=b]] = True

        # adjacency in both directions
        result = (temp | temp.T).astype(int)
        np.column_stack(np.nonzero(result))
        adj_list = [np.flatnonzero(row) for row in result[1:]]

        return adj_list

    def get_region_boundary(self, region_idx):
        '''
        Given a region, find tiles lying on its boundary
        Returns:
            boundary: ndarray of tiles
            binary_mask: 2d map with 1's for boundary and 0's for others
        '''
        # Convert map to a binary map by masking other regions
        binary_mask = np.where(self.map==region_idx, 1, 0)

        # use binary dilation to find outer 1's
        k = np.zeros((3,3),dtype=int); k[1] = 1; k[:,1] = 1
        binary_mask = binary_dilation(binary_mask==0, k) & binary_mask

        # Get outer 1's positions and transform to array
        x,y = np.where(binary_mask==1)
        boundary = np.vstack((x,y)).T
        return boundary, binary_mask #array[[x0,y0],[x1,y1],...]

    def is_adjacent(self, rid_1, rid_2):
        '''
        Given 2 regions, check if region_1 is adjacent to region_2
        '''
        return (rid_2 in self.adjacent_list[rid_1])

    def get_two_regions_boundary(self, rid_1, rid_2):
        '''
        Given 2 regions index, find their border
        '''
        # check if 2 regions are adjacent
        if rid_2 not in self.adjacent_list[rid_1]:
            return None

        r1_boundary, _ = self.get_region_boundary(rid_1)
        b1 = set()
        b2 = set()
        for tile in r1_boundary:
            col, row = tile
            if col+1 < self.width and self.map[col+1, row] == rid_2:
                b1.add((col, row))
                b2.add((col+1, row))
            if col-1 >= 0 and self.map[col-1, row] == rid_2:
                b1.add((col, row))
                b2.add((col-1, row))
            if row+1 < self.height and self.map[col, row+1] == rid_2:
                b1.add((col, row))
                b2.add((col, row+1))
            if row-1 >= 0 and self.map[col, row-1] == rid_2:
                b1.add((col, row))
                b2.add((col, row-1))

        return np.array(list(b1)), np.array(list(b2))
    
    def get_all_boundaries(self):
        '''
        Find every tiles lying on boundary of every region, except the sea
        '''
        binary_mask = np.zeros((self.width, self.height), dtype=bool)
        for i in range(1, self.num_regions+1):
            mask = self.get_region_boundary(i)
            binary_mask = np.logical_or(binary_mask, mask)
        
        sea = np.where(self.map==0, False, True)
        binary_mask = np.logical_and(binary_mask, sea)

        x,y = np.where(binary_mask==1)
        boundary = np.vstack((x,y)).T
        return boundary, binary_mask


    def is_movable(self,pos):
        '''
            Check if this cell is moveable (not mountain, sea)
        '''
        if pos[0] < 0 or pos[0] >= self.width or pos[1] < 0 or pos[1] >= self.height:
            return False
        return self.map[pos] != 0 and (np.array(pos) not in self.mountains)

    def check_column(self, col_idx):
        '''
        Check if treasure is on given column
        '''
        return col_idx == self.__treasure_pos[0]

    def check_row(self, row_idx):
        '''
        Check if treasure is on given row
        '''
        return row_idx == self.__treasure_pos[1]
    
    def check_rectangle_region(self, top_left, bot_right):
        '''
        Check if treasure is in a rectangle bounded by top_left and bot_right
        '''
        (x0, y0) = top_left
        (x1, y1) = bot_right
        (T_x, T_y) = self.__treasure_pos
        return T_x >= x0 and T_x <= x1 and T_y >= y0 and T_y <= y1
    
    def check_direction(self, pos, direction):
        (x,y) = pos
        (Tx, Ty) = self.__treasure_pos
        if direction=='East':
            if Tx < x:
                return False
            return (Ty <= y and Ty+Tx >= y+x) or (Ty > y and Tx-Ty >= x-y)
        elif direction == 'West':
            if Tx > x:
                return False
            return (Ty <= y and Tx-Ty <= x-y) or (Ty > y and Tx+Ty <= x+y)
        elif direction == 'North':
            if Ty > y:
                return False
            return (Tx <= x and Ty-Tx <= y-x) or (Tx > x and Ty+Tx <= y+x)
        elif direction == 'South':
            if Ty < y:
                return False
            return (Tx <= x and Ty+Tx >= y+x) or (Tx > x and Ty-Tx >= y-x)
        elif direction == 'South-East':
            return Tx >= x and Ty >= y
        elif direction == 'South-West':
            return Tx <= x and Ty >= y
        elif direction == 'North-East':
            return Tx >= x and Ty <= y
        else:
            return Tx <= x and Ty <= y

    def check_inside_gap(self, top_left_1, bot_right_1, top_left_2, bot_right_2) -> bool:
        (Tx, Ty) = self.__treasure_pos
        if not (Tx >= top_left_1[0] and Tx <= bot_right_1[0] and Ty >= top_left_1[1] and Ty <= bot_right_1[1]):
            return False
        if Tx >= top_left_2[0] and Tx <= bot_right_2[0] and Ty >= top_left_2[1] and Ty <= bot_right_2[1]:
            return False
        return True

    def check_on_all_boundaries(self) -> bool:
        '''
        Check if treasure lies on a boundary of any 2 regions
        '''
        (Tx, Ty) = self.__treasure_pos
        T_region = self.map[self.__treasure_pos]
        if Tx-1 >= 0 and self.map[Tx-1, Ty] != T_region:
            return True
        if Tx+1 < self.width and self.map[Tx+1, Ty] != T_region:
            return True
        if Ty-1 >= 0 and self.map[Tx, Ty-1] != T_region:
            return True
        if Ty+1 < self.height and self.map[Tx, Ty+1] != T_region:
            return True
        return False
    
    def check_on_specific_boundary(self, rid_1, rid_2) -> bool:
        '''
        Given 2 regions, check if treasure lies on their boundary
        '''
        (Tx, Ty) = self.__treasure_pos
        T_region = self.map[self.__treasure_pos]
        if T_region != rid_1 and T_region != rid_2:
            return False
        elif T_region == rid_1:
            return (Tx-1 >= 0 and self.map[Tx-1, Ty] == rid_2) or (Tx+1 < self.width and self.map[Tx+1, Ty] ==rid_2) or \
            (Ty-1 >= 0 and self.map[Tx, Ty-1] == rid_2) or (Ty+1 < self.height and self.map[Tx, Ty+1] == rid_2)
        else:
            return (Tx-1 >= 0 and self.map[Tx-1, Ty] == rid_1) or (Tx+1 < self.width and self.map[Tx+1, Ty] ==rid_1) or \
            (Ty-1 >= 0 and self.map[Tx, Ty-1] == rid_1) or (Ty+1 < self.height and self.map[Tx, Ty+1] == rid_1)
        return False

    def check_square_gap(self, big_square, small_square):
        #get the coordinates of tiles which has free y and be bounded by x (titles that are on top and bottom of gap created by 2 squares)
        bounded_col_tiles = np.stack(
                                np.meshgrid(
                                    [col for col in range(big_square[0] + 1, small_square[0])] + [col for col in range(small_square[2] + 1, big_square[2])], 
                                    [row for row in range(small_square[3], small_square[1] + 1)]
                                ), 
                                -1
                            ).reshape(-1, 2)

        #get the coordinates of tiles which has free x and be bounded by y (titles that are on 2 sides of gap created by 2 squares)
        #.append([row for row in range(row[1] + 1, row[0])]
        bounded_row_tiles = np.stack(
                                np.meshgrid(
                                    [col for col in range(big_square[0] + 1, big_square[2])], 
                                    [row for row in range(big_square[3] + 1, small_square[3])] + [row for row in range(small_square[1] + 1, big_square[1])]
                                ), 
                                -1
                            ).reshape(-1, 2)
        
        square_gap_tiles = np.concatenate((bounded_col_tiles, bounded_row_tiles), axis=0)

        hasTreasure = False
        if self.__treasure_pos in square_gap_tiles:
            hasTreasure = True

        return hasTreasure, square_gap_tiles
    
    def get_mountain_region(self):
        #get the list of regions which have mountain 
        return np.unique(self.map[self.mountains[:, 0], self.mountains[:, 1]])   

    def check_region(self, list_regions):
        region_tiles = None
        for region in list_regions:      
            if region_tiles is None:
                region_tiles = np.asarray(np.where(self.map == region)).T
            else:
                region_tiles = np.concatenate((region_tiles, np.asarray(np.where(self.map == region)).T), axis=0)
        
        hasTreasure = False
        if self.map[tuple(self.__treasure_pos)] in list_regions:
            hasTreasure = True
        
        return hasTreasure, region_tiles

    def check_rectangle(self, rectangle):
        #get the list of coordinates of titles which are inside the rectangle
        rectangle_tiles = np.stack(
                            np.meshgrid(
                                [col for col in range(rectangle[0] + 1, rectangle[2])], 
                                [row for row in range(rectangle[3] + 1, rectangle[1])]
                            ), 
                            -1
                        ).reshape(-1, 2) 
        
        hasTreasure = True
        #if the treasure is outside the rectangle, this hint is false
        if self.__treasure_pos[0] <= rectangle[0] or self.__treasure_pos[0] >= rectangle[2] or self.__treasure_pos[1] >= rectangle[1] or self.__treasure_pos[1] <= rectangle[3]:
            hasTreasure = False

        return hasTreasure, rectangle_tiles

    def convert_to_string(self, list):
        return ', '.join(map(str, list))

    def check_distance(self, agent_pos, pirate_pos):
        agent_distance = sum(abs(agent_pos[0] - self.__treasure_pos[0]), abs(agent_pos[1] - self.__treasure_pos[1]))
        pirate_distance = sum(abs(pirate_pos[0] - self.__treasure_pos[0]), abs(pirate_pos[1] - self.__treasure_pos[1]))
        
        isNearer = True
        if (agent_distance > pirate_distance):
            isNearer = False
        
        return isNearer
