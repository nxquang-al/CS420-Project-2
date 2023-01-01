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
        # Numpy array of mountaine array([m1, m2,...])
        self.mountains = []
        self.num_prisons = None
        # Numpy array of prisons array([p1, p2, p3,...])
        self.prisons = None

        self.input_region = random.randint(5, min(self.width, 7)) # including sea
        self.num_regions = self.input_region - 1 # number of lands

        # List of numpy array of adjacent regions
        self.adjacent_list = self.get_neighbors()

    def get_map_shape(self):
        return (self.width, self.height)

    def get_region(self, x, y):
        if x > 0 and x < self.height and y > 0 and y < self.height:
            return self.map[x, y]
        return 0

    def get_region_tiles(self, region_idx):
        return np.where(self.map == region_idx, 1, 0)

    def is_mountain(self, pos):
        # pos = np.asarray(pos)
        # return any(np.array_equal(pos, mountain) for mountain in self.mountains)
        return any([pos in self.mountains])

    def is_sea(self, pos):
        return self.map[pos] == 0

    def tile_type(self, x, y):
        if x > 0 and x < self.height and y > 0 and y < self.height:
            if self.is_mountain((x, y)) is True:
                return 'M'
            if (x, y) in self.prisons:
                return 'P'
            elif (x, y) == self.treasure_pos:
                return 'T'
        return ''

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
        num_regions_upper = self.input_region // 2

        start_x_upper = land_area//(num_regions_upper+1) + sea_size - 1
        start_y_upper = (self.height//2 - sea_size) // 2

        if region <= self.input_region//2:  # region on the upper half
            x = start_x_upper + (land_area // num_regions_upper)*(region-1)
            y = start_y_upper
            area = round(self.width // num_regions_upper)
        else:   # region on the lower half
            x = start_x_upper + (land_area // num_regions_upper) * \
                (region-num_regions_upper-1)
            y = start_y_upper + \
                (self.height//2 - start_y_upper)*2 - self.width//5
            area = round(self.width // (self.input_region -
                         num_regions_upper)*random.uniform(0.4, 1))

        if self.width > 30:
            y -= self.width//8

        return y, x, area

    def get_contiguous_region(self, x, y):
        '''
            Return a random adjacency region of the current cell
        '''
        possible_region = []
        if x > 0:
            possible_region.append(self.map[x-1, y])
        if y > 0:
            possible_region.append(self.map[x, y-1])
        if x < self.height - 1:
            possible_region.append(self.map[x+1, y])
        if y < self.width - 1:
            possible_region.append(self.map[x, y+1])

        filtered_region = [region for region in possible_region]

        if len(filtered_region) == 0:
            return 0

        region = np.random.choice(list(set(filtered_region)))
        return region

    def generate_map(self):
        '''
            Map generator
        '''
        if self.width < 16:
            sea_size = 1
        elif self.width < 32:
            sea_size = random.randint(2, 3)
        elif self.width < 64:
            sea_size = random.randint(2, 4)
        else:
            sea_size = random.randint(3, 6)

        self.map = self.map.astype(int)
        for region in range(1, self.input_region):
            queue = []
            center_x, center_y, area = self.get_region_center(sea_size, region)
            queue.append((center_x, center_y))
            self.map[center_x, center_y] = region

            avg_area = self.width*self.height//self.input_region
            region_size = random.randint(avg_area, round(avg_area*1.5))

            # Set the region of each cell using BFS
            while queue:
                x, y = queue.pop(0)
                region = self.map[x, y]
                current_size = 1

                # Check the adjacent cells and assign them the same region if they are empty
                for i in range(-x, area):
                    for j in range(-y, area):
                        new_x, new_y = x + i, y + j
                        if (new_x > 0 and new_x < self.width - sea_size and
                            new_y > 0 and new_y < self.height - sea_size
                            and (self.is_contiguous_region(new_x, new_y, region))
                                and current_size < region_size):

                            self.map[new_x, new_y] = region
                            current_size += 1

        # Randomize the number of mountains
        self.num_mountain = random.randint(5, max(round(self.width/4), 5))

        # Generate the mountains
        self.mountains = []
        while len(self.mountains) < self.num_mountain:
           # Randomize the size of the mountain
            size = random.randint(3, max(round(self.width/4), 4))

            # Generate the mountain cells
            mountain = []
            while True:
                x = random.randint(0, self.width - sea_size - 1)
                y = random.randint(0, self.height - sea_size - 1)
                if self.map[x, y] != 0:
                    mountain.append((x, y))
                    break

            for j in range(1, size):
                # Mountain can be diagonal adjacent to each other
                direction = np.array(
                    [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, 1], [1, 1], [1, -1], [-1, -1]])
                while True:
                    expand = random.randrange(8)
                    new_x, new_y = x + \
                        direction[expand, 0], y+direction[expand, 1]
                    if new_x > 0 and new_y > 0 and new_x < self.height - sea_size and new_y < self.width - sea_size:
                        if self.map[new_x, new_y] != 0:
                            mountain.append((new_x, new_y))
                            break

            # Add the mountain to the list
            for i in mountain:
                self.mountains.append(i)

        # Randomize the number of prisons
        self.num_prisons = random.randint(5, max(round(self.width/4), 5))

        # Generate the prisons
        self.prisons = []
        while len(self.prisons) < self.num_prisons:
            # Randomize the position of the prison
            while True:
                x = random.randint(0, self.width - sea_size - 2)
                y = random.randint(0, self.height - sea_size - 2)
                if self.map[x, y] != 0:
                    prison_overlap = False
                    # for mountain in self.mountains:
                    if (x, y) in self.mountains or (x,y) in self.prisons:
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
                # for mountain in self.mountains:
                if (x, y) in self.mountains:
                    treasure_overlap = True
                if (x, y) in self.prisons:
                    treasure_overlap = True
                if not treasure_overlap:
                    self.treasure_pos = (x, y)
                    break

        # Traverse the whole map to make sure that there is no uncontiguous cells
        # having the same region.
        for row in range(self.height):
            for col in range(self.width):
                if self.is_contiguous_region(row, col, self.map[row][col]) == False:
                    self.map[row][col] = self.get_contiguous_region(row, col)
                else:
                    if col > 0 and self.map[row][col] < self.map[row][col-1]:
                        self.map[row][col] = self.map[row][col-1]
                    temp_col = col
                    while temp_col+1 < self.width and self.map[row][temp_col+1] == 0:
                        self.map[row][temp_col +
                                      1] = self.get_contiguous_region(row, temp_col+1)
                        temp_col += 1

        # Set the border cells to region 0
        self.map[:, 0] = 0
        self.map[:, self.height - 1] = 0
        self.map[0, :] = 0
        self.map[self.width - 1, :], self.map[self.width - 2, :] = 0, 0

        # Make sea on the right goes random
        for i in range(self.height):
            sea = random.randint(2, 3)
            for j in range(self.width-1, self.width-sea, -1):
                if (i, j) not in self.mountains and (i, j) not in self.prisons and (i, j) != self.treasure_pos:
                    self.map[i, j] = 0
                else:
                    break

        # Initialize the output map
        output_map = np.empty((self.width, self.height), dtype='object')

        # Iterate through the map and add the mountain, prison, and treasure symbols
        for i in range(self.width):
            for j in range(self.height):
                region = self.map[i, j]
                output_map[i, j] = str(region)

                # Check if this cell is a mountain
                # for mountain in self.mountains:
                if (i, j) in self.mountains:
                    output_map[i, j] += 'M'
                    break

                # Check if this cell is a prison
                if (i, j) in self.prisons:
                    output_map[i, j] += 'P'

                # Check if this cell is the treasure
                if (i, j) == self.treasure_pos:
                    output_map[i, j] += 'T'

        print(f"Mountains: {self.mountains}")
        print(f"Prisons: {self.prisons}")
        print(f"Treasure: {self.treasure_pos}")
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
        # num_regions = int(self.map.max())
        num_regions = self.num_regions
        temp = np.zeros((num_regions+1, num_regions+1), dtype=bool)

        self.map = self.map.astype(int)

        # Check vertical adjacency
        a, b = self.map[:-1, :], self.map[1:, :]
        temp[a[a != b], b[a != b]] = True

        # Check horizontal adjacency
        a, b = self.map[:, :-1], self.map[:, 1:]
        temp[a[a != b], b[a != b]] = True

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
        binary_mask = np.where(self.map == region_idx, 1, 0)

        # use binary dilation to find outer 1's
        k = np.zeros((3, 3), dtype=int)
        k[1] = 1
        k[:, 1] = 1
        binary_mask = binary_dilation(binary_mask == 0, k) & binary_mask

        # Get outer 1's positions and transform to array
        x, y = np.where(binary_mask == 1)
        boundary = np.vstack((x, y)).T
        return boundary, binary_mask  # array[[x0,y0],[x1,y1],...]

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
        Return:
            tiles: array of boundary tiles
            binary_mask: a map represent boundary=1, others=0
        '''
        binary_mask = np.zeros((self.width, self.height), dtype=bool)
        for i in range(1, self.num_regions+1):
            _, mask = self.get_region_boundary(i)
            binary_mask = np.logical_or(binary_mask, mask)

        sea = np.where(self.map == 0, False, True)
        binary_mask = np.logical_and(binary_mask, sea)

        x, y = np.where(binary_mask == 1)
        tiles = np.vstack((x, y)).T
        return tiles, binary_mask

    def is_movable(self, pos):
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

    def check_direction(self, pos, direction):
        (x, y) = pos
        (Tx, Ty) = self.treasure_pos
        if direction == 'East':
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
            return (Tx-1 >= 0 and self.map[Tx-1, Ty] == rid_2) or (Tx+1 < self.width and self.map[Tx+1, Ty] == rid_2) or \
                (Ty-1 >= 0 and self.map[Tx, Ty-1] == rid_2) or (Ty +
                                                                1 < self.height and self.map[Tx, Ty+1] == rid_2)
        else:
            return (Tx-1 >= 0 and self.map[Tx-1, Ty] == rid_1) or (Tx+1 < self.width and self.map[Tx+1, Ty] == rid_1) or \
                (Ty-1 >= 0 and self.map[Tx, Ty-1] == rid_1) or (Ty +
                                                                1 < self.height and self.map[Tx, Ty+1] == rid_1)
        return False

    def check_square_gap(self, big_square, small_square):
        # get the coordinates of tiles which are inside the big square (not include titles on the edge)
        big_square_tiles = np.stack(
            np.meshgrid(
                [col for col in range(big_square[0] + 1, big_square[2])],
                [row for row in range(
                    big_square[1] + 1, big_square[3])]
            ),
            -1
        ).reshape(-1, 2)

        # get the coordinates of tiles which are inside the small square (include titles on the edge)
        small_square_tiles = np.stack(
            np.meshgrid(
                [col for col in range(small_square[0], small_square[2] + 1)],
                [row for row in range(
                    small_square[1], small_square[3] + 1)]
            ),
            -1
        ).reshape(-1, 2)

        # remove all the small_square_tiles from the big_square_tiles
        mask = np.array([not np.any(np.equal(tile, small_square_tiles).all(1))
                        for tile in big_square_tiles])
        square_gap_tiles = big_square_tiles[mask]

        hasTreasure = True
        if (self.treasure_pos[0] >= small_square[0] and self.treasure_pos[0] <= small_square[2] and self.treasure_pos[1] >= small_square[1] and self.treasure_pos[1] <= small_square[3]) or (self.treasure_pos[0] <= big_square[0] or self.treasure_pos[0] >= big_square[2] or self.treasure_pos[1] <= big_square[1] or self.treasure_pos[1] >= big_square[3]):
            hasTreasure = False

        return hasTreasure, square_gap_tiles

    def get_mountain_region(self):
        # get the list of regions which have mountain
        return np.unique(self.map[list(self.mountains)[:, 0], list(self.mountains)[:, 1]])

    def check_region(self, list_regions):
        region_tiles = None
        for region in list_regions:
            if region_tiles is None:
                region_tiles = np.asarray(np.where(self.map == region)).T
            else:
                region_tiles = np.concatenate(
                    (region_tiles, np.asarray(np.where(self.map == region)).T), axis=0)

        hasTreasure = False
        if self.map[self.treasure_pos[0], self.treasure_pos[1]] in list_regions:
            hasTreasure = True

        return hasTreasure, region_tiles

    def check_rectangle(self, rectangle):
        # get the list of coordinates of titles which are inside the rectangle
        rectangle_tiles = np.stack(
            np.meshgrid(
                [col for col in range(rectangle[0] + 1, rectangle[2])],
                [row for row in range(
                    rectangle[1] + 1, rectangle[3])]
            ),
            -1
        ).reshape(-1, 2)

        hasTreasure = True
        # if the treasure is outside the rectangle, this hint is false
        if self.treasure_pos[0] <= rectangle[0] or self.treasure_pos[0] >= rectangle[2] or self.treasure_pos[1] <= rectangle[1] or self.treasure_pos[1] >= rectangle[3]:
            hasTreasure = False

        return hasTreasure, rectangle_tiles

    def check_distance(self, agent_pos, pirate_pos):
        agent_distance = abs(
            agent_pos[0] - self.treasure_pos[0]) + abs(agent_pos[-1] - self.treasure_pos[1])
        pirate_distance = abs(
            pirate_pos[0] - self.treasure_pos[0]) + abs(pirate_pos[-1] - self.treasure_pos[1])

        nearer_tiles = np.stack(
            np.meshgrid(
                [col for col in range(self.width)],
                [row for row in range(self.height)]
            ),
            -1
        ).reshape(-1, 2)

        col = nearer_tiles[:, 0]
        row = nearer_tiles[:, 1]
        mask = (abs(agent_pos[0] - col) + abs(agent_pos[1] - row)
                ) < (abs(pirate_pos[0] - col) + abs(pirate_pos[1] - row))
        nearer_tiles = nearer_tiles[mask]

        isNearer = False
        if (agent_distance < pirate_distance):
            isNearer = True

        return isNearer, nearer_tiles

    def convert_to_string(self, list):
        return ', '.join(map(str, list))