import numpy as np
from scipy.ndimage import binary_dilation
import random
import math

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

        self.num_regions = random.randint(4, min(self.width, 7))
        self.adjacent_list = self.get_neighbors()    # List of numpy array of adjacent regions
    
    def get_map_shape(self):
        return (self.width, self.height)
    
    def is_contiguous_region(self, x, y, region):
        '''
            Check if the adjacent cell belongs to the same region
        '''
        return (
            (x > 0 and self.map[x-1, y] == region) 
            or (x < self.height - 1 and self.map[x+1, y] == region)
            or (y > 0 and self.map[x, y-1] == region)
            or (y < self.width - 1 and self.map[x, y+1] == region))

    def get_region_center(self, sea_size, region):
        '''
            Get the center coordinate of a region
        '''
        land_area = self.width - sea_size*2
        num_regions_upper = self.num_regions // 2

        start_x_upper = land_area//(num_regions_upper+1) + sea_size - 1
        start_y_upper = (self.height//2 - sea_size) //2

        if region <= self.num_regions//2:  # region on the upper half 
            x = start_x_upper + (land_area // num_regions_upper)*(region-1)
            y = start_y_upper
            area = round(self.width // num_regions_upper)
        else:   # region on the lower half
            x = start_x_upper + (land_area // num_regions_upper)*(region-num_regions_upper-1)
            y = start_y_upper + (self.height//2 - start_y_upper)*2 - self.width//5
            area = round(self.width // (self.num_regions - num_regions_upper)*random.uniform(0.4, 1)) 
        
        if self.width > 30:
            y -= self.width//8

        return y, x, area

    def get_contiguous_region(self, x, y):
        '''
            Return a random adjacency region of the current cell
        '''
        possible_region =  []
        if x > 0: possible_region.append(self.map[x-1, y]) 
        if y > 0: possible_region.append(self.map[x, y-1])
        if x < self.height - 1: possible_region.append(self.map[x+1, y])
        if y < self.width - 1: possible_region.append(self.map[x, y+1])
        
        filtered_region = [region for region in possible_region]

        if len(filtered_region) == 0: return 0

        region = np.random.choice(list(set(filtered_region)))
        return region
    
    def is_contiguous_region(self, x, y, region):
        '''
            Check if the adjacent cell belongs to the same region
        '''
        return (
            (x > 0 and self.map[x-1, y] == region) 
            or (x < self.height - 1 and self.map[x+1, y] == region)
            or (y > 0 and self.map[x, y-1] == region)
            or (y < self.width - 1 and self.map[x, y+1] == region))

    def get_region_center(self, sea_size, region):
        '''
            Get the center coordinate of a region
        '''
        land_area = self.width - sea_size*2
        num_regions_upper = self.num_regions // 2

        start_x_upper = land_area//(num_regions_upper+1) + sea_size - 1
        start_y_upper = (self.height//2 - sea_size) //2

        if region <= self.num_regions//2:  # region on the upper half 
            x = start_x_upper + (land_area // num_regions_upper)*(region-1)
            y = start_y_upper
            area = round(self.width // num_regions_upper)
        else:   # region on the lower half
            x = start_x_upper + (land_area // num_regions_upper)*(region-num_regions_upper-1)
            y = start_y_upper + (self.height//2 - start_y_upper)*2 - self.width//5
            area = round(self.width // (self.num_regions - num_regions_upper)*random.uniform(0.4, 1)) 
        
        if self.width > 30:
            y -= self.width//8

        return y, x, area

    def get_contiguous_region(self, x, y):
        '''
            Return a random adjacency region of the current cell
        '''
        possible_region =  []
        if x > 0: possible_region.append(self.map[x-1, y]) 
        if y > 0: possible_region.append(self.map[x, y-1])
        if x < self.height - 1: possible_region.append(self.map[x+1, y])
        if y < self.width - 1: possible_region.append(self.map[x, y+1])
        
        filtered_region = [region for region in possible_region]

        if len(filtered_region) == 0: return 0

        region = np.random.choice(list(set(filtered_region)))
        return region
    
    def generate_map(self):
        '''
            Map generator
        '''
        if self.width < 16: sea_size = 1
        elif self.width < 32: sea_size = random.randint(1,3)
        elif self.width < 64: sea_size = random.randint(2,4)
        else: sea_size = random.randint(3,6)

        

        self.map = self.map.astype(int)

        for region in range (1, self.num_regions):
            queue = []
            center_x, center_y, area = self.get_region_center(sea_size, region)
            queue.append((center_x, center_y))
            self.map[center_x, center_y] = region

            avg_area = self.width*self.height//self.num_regions
            region_size = random.randint(avg_area, round(avg_area*1.5))

            # Set the region of each cell using BFS
            while queue:
                x, y = queue.pop(0)
                region = self.map[x, y]
                current_size = 1

                # Check the adjacent cells and assign them the same region if they are empty
                for i in range(-x, area + sea_size):
                    # area = random.randint(region_rows, region_rows+6)
                    for j in range(-y, area + sea_size):
                        new_x, new_y = x + i, y + j
                        if (new_x > 0 and new_x < self.width - sea_size and 
                            new_y > 0 and new_y < self.height - sea_size 
                            and (self.is_contiguous_region(new_x, new_y, region))
                            and current_size < region_size): 

                            self.map[new_x, new_y] = region
                            current_size+=1
        
        # Randomize the number of mountains
        self.num_mountain = random.randint(self.num_regions, self.num_regions + 6)
            
        # Generate the mountains
        self.mountains = []
        for i in range(self.num_mountain):
           # Randomize the size of the mountain
            size = random.randint(5, 8)

            # Generate the mountain cells
            mountain = []
            while True:
                x = random.randint(0, self.width - sea_size)
                y = random.randint(0, self.height - sea_size)
                if self.map[x, y] != 0:
                    mountain.append((x, y))
                    break 

            for j in range(1, size):
                # Mountain can be diagonal adjacent to each other
                direction = np.array([[-1, 0], [1, 0], [0, -1], [0, 1], [-1, 1], [1, 1], [1, -1], [-1, -1]])
                while True:
                    expand = random.randrange(8)
                    new_x, new_y = x+direction[expand,0], y+direction[expand,1]
                    if new_x > 0 and new_y > 0 and new_x < self.height and new_y < self.width:
                        if self.map[new_x, new_y] != 0:
                            mountain.append((new_x, new_y))
                            break

            # Add the mountain to the list
            self.mountains.append(mountain)

        # Randomize the number of prisons
        self.num_prisons = random.randint(self.num_regions-1, self.num_regions + 3)

        # Generate the prisons
        self.prisons = []
        for i in range(self.num_prisons):
            # Randomize the position of the prison
            while True:
                x = random.randint(0, self.width - sea_size)
                y = random.randint(0, self.height - sea_size)
                if self.map[x, y] != 0:
                    prison_overlap = False
                    for mountain in self.mountains:
                        if (x, y) in mountain:
                            prison_overlap = True
                            break
                    if not prison_overlap:
                        self.prisons.append((x, y))
                        break

        # Randomize the position of the treasure
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.map[x, y] != 0:
                # Check if the treasure is not on top of a mountain or prison
                treasure_overlap = False
                for mountain in self.mountains:
                    if (x, y) in mountain:
                        treasure_overlap = True
                        break
                if (x, y) in self.prisons:
                    treasure_overlap = True
                if not treasure_overlap:
                    self.treasure_pos = (x, y)
                    break
                
        # Traverse the whole map to make sure that there is no uncontiguous cells
        # having the same region.
        for row in range (self.height):
            for col in range(self.width):
                if self.is_contiguous_region(row, col, self.map[row][col]) == False:
                    self.map[row][col] = self.get_contiguous_region(row, col)
                else:
                    if col > 0 and self.map[row][col] < self.map[row][col-1]:
                        self.map[row][col] = self.map[row][col-1]
                    temp_col = col
                    while temp_col+1 < self.width and self.map[row][temp_col+1] == 0:
                        self.map[row][temp_col+1] = self.get_contiguous_region(row, temp_col+1)
                        temp_col+=1
        
        # Set the border cells to region 0
        self.map[:, 0] = 0
        self.map[:, self.height - 1], self.map[:, self.height - 2] = 0, 0
        self.map[0, :] = 0
        self.map[self.width - 1, :], self.map[self.width - 2, :] = 0, 0

        # Initialize the output map
        output_map = np.empty((self.width, self.height), dtype='object')

        # Iterate through the map and add the mountain, prison, and treasure symbols
        for i in range(self.width):
            for j in range(self.height):
                region = self.map[i, j]
                output_map[i, j] = str(region)

                # Check if this cell is a mountain
                for mountain in self.mountains:
                    if (i, j) in mountain:
                        output_map[i, j] += 'M'
                        break

                # Check if this cell is a prison
                if (i, j) in self.prisons:
                    output_map[i, j] += 'P'

                # Check if this cell is the treasure
                if (i, j) == self.treasure_pos:
                    output_map[i, j] += 'T'

        # Return the output map
        return output_map

    def get_regions__of_mountains(self):
        '''
            For the 14th hint
        '''
        return

    def get_neighbors(self):
        '''
        This function finds adjacent regions of each region
        Return: list of N items, N is the number of regions
                Each item is a ndarray of indexes of adjacent regions
                [array([r1, r2]), array[r3, r4],...]

        '''
        num_regions = int(self.map.max())
        temp = np.zeros((num_regions+1, num_regions+1), dtype=bool)

        self.map = self.map.astype(int)

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

    def is_adjacent(self, rid_1, rid_2):
        '''
        Given 2 regions, check if region_1 is adjacent to region_2
        '''
        return (rid_2 in self.adjacent_list[rid_1])

    def get_two_regions_boundary(self, rid_1, rid_2):
        '''
        Given 2 regions index, find their boudary tiles
        '''
        # check if 2 regions are adjacent
        if rid_2 not in self.adjacent_list[rid_1]:
            return None

        r1_boundary = self.get_region_boundary(rid_1)
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

    def isMovable(self,col,row):
        '''
            Check if this cell is moveable (not mountain, sea)
        '''
        return self.map[col, row] != 0 and ([col, row] not in self.mountains)

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
        (Tx, Ty) = self.treasure_pos
        if not (Tx >= top_left_1[0] and Tx <= bot_right_1[0] and Ty >= top_left_1[1] and Ty <= bot_right_1[1]):
            return False
        if Tx >= top_left_2[0] and Tx <= bot_right_2[0] and Ty >= top_left_2[1] and Ty <= bot_right_2[1]:
            return False
        return True

    def check_on_all_boundaries(self) -> bool:
        '''
        Check if treasure lies on a boundary of any 2 regions
        '''
        (Tx, Ty) = self.treasure_pos
        T_region = self.map[self.treasure_pos]
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
        (Tx, Ty) = self.treasure_pos
        T_region = self.map[self.treasure_pos]
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
        if self.treasure_pos in square_gap_tiles:
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
        if self.map[tuple(self.treasure_pos)] in list_regions:
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
        if self.treasure_pos[0] <= rectangle[0] or self.treasure_pos[0] >= rectangle[2] or self.treasure_pos[1] >= rectangle[1] or self.treasure_pos[1] <= rectangle[3]:
            hasTreasure = False

        return hasTreasure, rectangle_tiles

    def convert_to_string(self, list):
        return ', '.join(map(str, list))

    def check_distance(self, agent_pos, pirate_pos):
        agent_distance = sum(abs(agent_pos[0] - self.treasure_pos[0]), abs(agent_pos[1] - self.treasure_pos[1]))
        pirate_distance = sum(abs(pirate_pos[0] - self.treasure_pos[0]), abs(pirate_pos[1] - self.treasure_pos[1]))
        
        isNearer = True
        if (agent_distance > pirate_distance):
            isNearer = False
        
        return isNearer


N = 32
map = Map(N,N)

def parse_grid(grid_string):
    # Split string into rows
    rows = grid_string.strip().split("\n")

    # Split rows into cells
    cells = [row.split() for row in rows]

   # Convert cells to strings
    return [[cell[1] if len(cell) == 2 else cell for cell in row] for row in cells]

def visualize_grid(grid, n):
    # Map values to colors
    colors = {
        "T": "\033[41m",  # highlighted red 
        "M": "\033[45m",  # highlighted purple
        "P": "\033[42m",  # highlighted green
        "0": "\033[34m",  # blue
        "1": "\033[33m",  # yellow
        "2": "\033[31m",  # red
        "3": "\033[37m",  # white
        "4": "\033[32m",  # green
        "5": "\033[28m",  # gray
        "6": "\033[38;5;208m",  # orange
        "7": "\033[36m",  # cyan
    }

   # Initialize visualization as a list of empty strings
    vis = ["" for i in range(n)]

    # Iterate over rows and columns
    for i in range(n):
        for j in range(n):
            # Get color for value
            color = colors.get(grid[i][j], "\033[35m")  # purple for other values

            # Append colored character to visualization
            vis[i] += color + grid[i][j] + "\033[0m"

    # Join rows of visualization into a single string
    return "\n".join(vis)

res = ""
output_map = map.generate_map()
for row in output_map:
    res += (' '.join(row))
    res += '\n'

grid = parse_grid(res)

res = map.generate_map()
for row in res:
    print(' '.join(row))

print(visualize_grid(grid, N))