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
        self.treasure_pos = None

        self.num_mountain = None
        self.mountains = []                         # Numpy array of mountaine array([m1, m2,...])
        self.num_prisons = None
        self.prisons =  None                        # Numpy array of prisons array([p1, p2, p3,...])

        self.num_regions = None
        self.adjacent_list = self.get_adjacent()    # List of numpy array of adjacent regions
        self.region_boundaries = []                 # List of numpy array [bound_region_1, bound_region_2,...]

        for i in range(self.num_regions):
            self.region_boundaries.append(self.get_region_boundary(i))
    
    def get_map_shape(self):
        return self.width, self.height
    
    def generate_map(self):
        return
    
    def get_regions__of_mountains(self):
        '''
            For the 14th hint
        '''
        return

    def get_adjacent(self):
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
        Given a region, returns an array of its boundary tiles
        '''
        # Convert map to a binary map by masking other regions
        binary_mask = np.where(self.map==region_idx, 1, 0)

        # use binary dilation to find outer 1's
        k = np.zeros((3,3),dtype=int); k[1] = 1; k[:,1] = 1
        binary_mask = binary_dilation(binary_mask==0, k) & binary_mask

        # Get outer 1's positions and transform to array
        x,y = np.where(binary_mask==1)
        boundary = np.vstack((x,y)).T
        return boundary #array[[x0,y0],[x1,y1],...]

    def isMovable(self,col,row):
        '''
            Check if this cell is moveable (not mountain, sea)
        '''
        return

    def check_column(self, col_idx):
        '''
        Check if treasure is on given column
        '''
        return col_idx == self.treasure_pos[0]

    def check_row(self, row_idx):
        '''
        Check if treasure is on given row
        '''
        return row_idx == self.treasure_pos[1]
    
    def check_rectangle_region(self, top_left, bot_right):
        '''
        Check if treasure is in a rectangle bounded by top_left and bot_right
        '''
        (x0, y0) = top_left
        (x1, y1) = bot_right
        (T_x, T_y) = self.treasure_pos
        return T_x >= x0 and T_x <= x1 and T_y >= y0 and T_y <= y1
    
    def check_direction(self, prison_pos, direction):
        (x,y) = prison_pos
        (Tx, Ty) = self.treasure_pos
        if direction=='E':
            if Tx < x:
                return False
            return (Ty <= y and Ty+Tx >= y+x) or (Ty > y and Tx-Ty >= x-y)
        elif direction == 'W':
            if Tx > x:
                return False
            return (Ty <= y and Tx-Ty <= x-y) or (Ty > y and Tx+Ty <= x+y)
        elif direction == 'N':
            if Ty > y:
                return False
            return (Tx <= x and Ty-Tx <= y-x) or (Tx > x and Ty+Tx <= y+x)
        elif direction == 'S':
            if Ty < y:
                return False
            return (Tx <= x and Ty+Tx >= y+x) or (Tx > x and Ty-Tx >= y-x)
        elif direction == 'SE':
            return Tx >= x and Ty >= y
        elif direction == 'SW':
            return Tx <= x and Ty >= y
        elif direction == 'NE':
            return Tx >= x and Ty <= y
        else:
            return Tx <= x and Ty <= y

    def check_inside_gap(self, top_left_1, bot_right_1, top_left_2, bot_right_2):
        Tx, Ty = self.treasure_pos
        if not (Tx >= top_left_1[0] and Tx <= bot_right_1[0] and Ty >= top_left_1[1] and Ty <= bot_right_1[1]):
            return False
        if Tx >= top_left_2[0] and Tx <= bot_right_2[0] and Ty >= top_left_2[1] and Ty <= bot_right_2[1]:
            return False
        return True

    def check_on_boundary(self):
        '''
        Check if treasure lies on a boundary
        '''
        (Tx, Ty) = self.treasure_pos
        T_region = self.map[Tx, Ty]
        if Tx-1 >= 0 and self.map[Tx-1, Ty] != T_region:
            return True
        if Tx+1 < self.width and self.map[Tx+1, Ty] != T_region:
            return True
        if Ty-1 >= 0 and self.map[Tx, Ty-1] != T_region:
            return True
        if Ty+1 < self.height and self.map[Tx, Ty+1] != T_region:
            return True
        return False

   
    def check_adjancent_regions(self, rid_1, rid_2):
        '''
        Given 2 regions, check if they are adjacent
        '''
        return

    
    
    
