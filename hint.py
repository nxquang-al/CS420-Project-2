import numpy as np
import random
from map import Map


class HintManager:
    def __init__(self, map: Map):
        self.map = map
        self.agent_pos = None
        self.pirate_pos = None
        return

    def generate(self,agent_pos, pirate_pos, hint_weights):
        '''
        Return a random hint with its truth value
        '''
        # need to update to get the latest positions of the agent and pirate so we can generate the 6th typed hint
        self.agent_pos = agent_pos
        self.pirate_pos = pirate_pos

        hint_type = random.choices(range(1, 16), weights=hint_weights, k=1)[0]
        if (hint_type == 1):
            return self.gen_1st_type()
        elif (hint_type == 2):
            return self.gen_2nd_type()
        elif (hint_type == 3):
            return self.gen_3rd_type()
        elif (hint_type == 4):
            return self.gen_4th_type()
        elif (hint_type == 5):
            return self.gen_5th_type()
        elif (hint_type == 6):
            return self.gen_6th_type()
        elif (hint_type == 7):
            return self.gen_7th_type()
        elif (hint_type == 8):
            return self.gen_8th_type()
        elif (hint_type == 9):
            return self.gen_9th_type()
        elif (hint_type == 10):
            return self.gen_10th_type()
        elif (hint_type == 11):
            return self.gen_11th_type()
        elif (hint_type == 12):
            return self.gen_12th_type()
        elif (hint_type == 13):
            return self.gen_13th_type(self.pirate_pos)
        elif (hint_type == 14):
            return self.gen_14th_type()
        else:
            return self.gen_15th_type()

    def gen_first_hint(self, agent_pos, pirate_pos, hint_weights):
        '''
        generate the first hint, which is always true
        '''
        self.agent_pos = agent_pos
        self.pirate_pos = pirate_pos

        hint_type = random.choices(range(1, 16), weights=hint_weights, k=1)[0]
        truth_val = False

        while not truth_val:
            if (hint_type == 1):
                hint_type, log, truth_val, data = self.gen_1st_type()
            elif (hint_type == 2):
                hint_type, log, truth_val, data = self.gen_2nd_type()
            elif (hint_type == 3):
                hint_type, log, truth_val, data = self.gen_3rd_type()
            elif (hint_type == 4):
                hint_type, log, truth_val, data = self.gen_4th_type()
            elif (hint_type == 5):
                hint_type, log, truth_val, data = self.gen_5th_type()
            elif (hint_type == 6):
                hint_type, log, truth_val, data = self.gen_6th_type()
            elif (hint_type == 7):
                hint_type, log, truth_val, data = self.gen_7th_type()
            elif (hint_type == 8):
                hint_type, log, truth_val, data = self.gen_8th_type()
            elif (hint_type == 9):
                hint_type, log, truth_val, data = self.gen_9th_type()
            elif (hint_type == 10):
                hint_type, log, truth_val, data = self.gen_10th_type()
            elif (hint_type == 11):
                hint_type, log, truth_val, data = self.gen_11th_type()
            elif (hint_type == 12):
                hint_type, log, truth_val, data = self.gen_12th_type()
            elif (hint_type == 13):
                hint_type, log, truth_val, data = self.gen_13th_type(
                    self.pirate_pos)
            elif (hint_type == 14):
                hint_type, log, truth_val, data = self.gen_14th_type()
            else:
                hint_type, log, truth_val, data = self.gen_15th_type()

        return hint_type, log, truth_val, data

    def gen_1st_type(self):
        '''
        A list of random tiles that doesn't contain the treasure (1 to 12)
        '''
        # random the number of random tiles 1 - 12
        num_tiles = np.random.randint(
            1, min(13, self.map.width * self.map.height + 1))

        # random the num_tiles ordinal number of tiles and then convert to coordinates of tiles
        ordinal_num_tiles = np.random.choice(
            np.arange(self.map.width * self.map.height), (num_tiles,), replace=False)

        col = ordinal_num_tiles % self.map.width
        row = ordinal_num_tiles // self.map.width

        array_of_tiles = np.column_stack((col, row))

        log = "A list of tiles [{}] doesn't contain the treasure".format(
            self.map.convert_to_string(array_of_tiles))

        truth = True
        # check if array_of_tiles contain treasure_pos, wwe have to check by this way instead of using "in"
        if np.any(np.equal(self.map.treasure_pos, array_of_tiles).all(1)):
            truth = False

        return 1, log, truth, array_of_tiles

    def gen_2nd_type(self):
        '''
        2-5 regions that 1 of them has the treasure.
        '''
        num_regions = np.random.randint(2, min(6, self.map.num_regions + 1))

        list_regions = np.random.choice(
            np.arange(1, self.map.num_regions + 1), (num_regions,), replace=False)

        log = "One of the regions {} has the treasure".format(
            self.map.convert_to_string(list_regions))

        truth, _ = self.map.check_region(list_regions)

        return 2, log, truth, list_regions

    def gen_3rd_type(self):
        '''
        1-3 regions that do not contain the treasure.
        '''
        num_regions = np.random.randint(1, min(4, self.map.num_regions + 1))

        list_regions = np.random.choice(
            np.arange(1, self.map.num_regions), (num_regions,), replace=False)

        log = "Regions {} do not contain the treasure".format(
            self.map.convert_to_string(list_regions))

        truth, _ = self.map.check_region(list_regions)

        return 3, log, (not truth), list_regions

    def gen_4th_type(self):
        '''
        A large rectangle area that has the treasure.
        '''
        map_area = self.map.width * self.map.height
        rectangle = None

        while True:
            # choose 2 coordinates x from 0 - width and sort ascending
            col = np.sort(np.random.choice(np.arange(self.map.width), (2,)))
            # choose 2 coordinates y from 0 - height and sort ascending
            row = np.sort(np.random.choice(np.arange(self.map.height), (2,)))

            selected_area = (col[1] - col[0]) * (row[1] - row[0])

            # large rectangle area is an area that must be as big as 50% - 70% total area of the map
            if selected_area >= 0.5 * map_area and selected_area < 0.7 * map_area:
                # this array has 4 elements representing for rectangle's coordinates [top_left_x, bottom_right_x, top_left_y, bottom_right_y]
                rectangle = np.array([col[0], row[0], col[1], row[1]])
                break

        log = "A large rectangle area has the treasure. Top-Left-Bottom-Right = [{}]".format(
            self.map.convert_to_string(rectangle))

        truth, array_of_tiles = self.map.check_rectangle(rectangle)

        return 4, log, truth, array_of_tiles

    def gen_5th_type(self):
        '''
        A small rectangle area that doesn't has the treasure.
        '''
        map_area = self.map.width * self.map.height
        rectangle = None

        while True:
            # choose 2 coordinates x from 0 - width and sort ascending
            col = np.sort(np.random.choice(np.arange(self.map.width), (2,)))
            # choose 2 coordinates y from 0 - height and sort ascending
            row = np.sort(np.random.choice(np.arange(self.map.height), (2,)))

            selected_area = (col[1] - col[0]) * (row[1] - row[0])

            # large rectangle area is an area that must be as big as 20% - 50% total area of the map
            if selected_area >= 0.2 * map_area and selected_area < 0.5 * map_area:
                # this array has 4 elements representing for rectangle's coordinates [top_left_x, bottom_right_x, top_left_y, bottom_right_y]
                rectangle = np.array([col[0], row[0], col[1], row[1]])
                break

        log = "A small rectangle area doesn't has the treasure. Top-Left-Bottom-Right = [{}]".format(
            self.map.convert_to_string(rectangle))

        truth, array_of_tiles = self.map.check_rectangle(rectangle)

        return 5, log, not truth, array_of_tiles

    def gen_6th_type(self):
        '''
        He tells you that you are the nearest person to the treasure (between
        you and the prison he is staying).
        '''
        log = "The agent is nearer than the pirate to the treasure"

        truth, array_of_tiles = self.map.check_distance(
            self.agent_pos, self.pirate_pos)

        return 6, log, truth, None

    def gen_7th_type(self):
        '''
        A column and/or a row that contain the treasure (rare).
        '''
        width, height = self.map.get_map_shape()
        # Option: 0 - only column, 1 - only row, 2 - both
        choice = np.random.choice([0, 1, 2], p=[0.45, 0.45, 0.1], size=1)[0]
        c, r = None, None
        log = ''
        truth = False
        if choice == 0:
            # Column
            c = random.randint(0, width)
            truth = self.map.check_column(c)
            log = 'Column {} contains the treasure'.format(c)
        elif choice == 1:
            # Row
            r = random.randint(0, height)
            truth = self.map.check_row(r)
            log = 'Row {} contains the treasure'.format(r)
        elif choice == 2:
            # Both
            c = random.randint(0, width)
            r = random.randint(0, height)
            truth = self.map.check_column(c) and self.map.check_row(r)
            log = 'Column {} and row {} contain the treasure'.format(c, r)

        return 7, log, truth, np.array([c, r])

    def gen_8th_type(self):
        '''
        A column and/or a row that do not contain the treasure.
        '''
        width, height = self.map.get_map_shape()
        choice = np.random.choice([0, 1, 2], p=[0.45, 0.45, 0.1], size=1)[0]
        c = r = None
        truth = False
        if choice == 0:
            # Column
            c = random.randint(0, width)
            # column = np.expand_dims(np.arange(0,height), axis=1)
            # column = np.pad(column, (1,0), 'constant', constant_values=c)
            log = 'Column {} does not contain the treasure'.format(c)
            truth = not self.map.check_column(c)
        elif choice == 1:
            # Row
            r = random.randint(0, height)
            log = 'Row {} does not contain the treasure'.format(r)
            truth = not self.map.check_row(r)
        elif choice == 2:
            # Both
            c = random.randint(0, width)
            r = random.randint(0, height)
            log = 'Column {} and row {} do not contain the treasure'.format(
                c, r)
            truth = not self.map.check_column(c) and not self.map.check_row(r)
        return 8, log, truth, np.array([c, r])

    def gen_9th_type(self):
        '''
        2 regions that the treasure is somewhere in their boundary.
        '''
        rid_1 = random.randint(0, self.map.num_regions-1)
        rand_idx = np.random.choice(
            self.map.adjacent_list[rid_1].shape[0], size=1, replace=False)[0]

        rid_2 = self.map.adjacent_list[rid_1][rand_idx]

        log = 'Treasure is somewhere in the boundary of regions {} and {}.'.format(
            rid_1, rid_2)
        truth = self.map.check_on_specific_boundary(rid_1, rid_2)

        return 9, log, truth, np.array([rid_1, rid_2])

    def gen_10th_type(self):
        '''
        The treasure is somewhere in a boundary of 2 regions
        '''
        log = 'The treasure is somewhere in a boundary of 2 regions'
        truth = self.map.check_on_all_boundaries()
        return 10, log, truth, None

    def gen_11th_type(self):
        '''
        The treasure is somewhere in an area bounded by 1-3 tiles from sea.
        '''
        num_tiles = random.randint(2, 3)
        log = 'The treasure is somewhere in an area bounded by {num_tiles} tiles from sea'

        sea = np.where(self.map == 0, True, False)
        not_sea = np.logical_not(sea)
        binary_mask = np.zeros(self.map.get_map_shape(), bool)

        for _ in range(num_tiles):
            upward = np.roll(sea, -1, axis=0)
            upward[-1,] = False

            downward = np.roll(sea, shift=1, axis=0)
            downward[0,] = False

            leftward = np.roll(sea, shift=-1, axis=1)
            leftward[:, -1] = False

            rightward = np.roll(sea, shift=1, axis=1)
            rightward[:, 0] = 0

            sea = upward + downward + leftward + rightward
            binary_mask += sea

        binary_mask &= not_sea
        truth = binary_mask[self.map.treasure_pos]

        return 11, log, truth, binary_mask

    def gen_12th_type(self):
        '''
        A half of the map without treasure (rare).
        '''
        width, height = self.map.get_map_shape()
        choice = random.randint(0, 3)  # 0: left, 1: right, 2: top, 3: right
        if choice == 0:  # left half
            top_left = (0, 0)
            bot_right = (width // 2, height)
            log = 'The left half of the map does not contains treasure'
        elif choice == 1:  # right half
            top_left = (width // 2, 0)
            bot_right = (width, height)
            log = 'The right half of the map does not contains treasure'
        elif choice == 3:  # top half
            top_left = (0, 0)
            bot_right = (width, height // 2)
            log = 'The top half of the map does not contains treasure'
        else:  # bottom half
            top_left = (0, height // 2)
            bot_right = (width, height)
            log = 'The bottom half of the map does not contains treasure'

        truth = self.map.check_rectangle_region(top_left, bot_right)
        return 12, log, truth, np.array([top_left, bot_right])

    def gen_13th_type(self, pos):
        '''
        From the position that he's staying, he tells
        you a direction that has the treasure (W, E, N, S or SE, SW, NE, NW)
        (The shape of area when the hints are either W, E, N or S is triangle).
        '''
        choice = random.randint(0, 7)
        mask = np.zeros(self.map.get_map_shape(), dtype=bool)
        if choice == 0:
            direction = 'East'
            for y in range(mask.shape[1]):
                if y <= pos[1]:
                    idx = pos[0] + pos[1] - y
                else:
                    idx = y - pos[1] + pos[0]
                mask[idx:, y] = 1
        elif choice == 1:
            direction = 'West'
            for y in range(mask.shape[1]):
                if y <= pos[1]:
                    idx = y - pos[1] + pos[0]
                else:
                    idx = pos[0] + pos[1] - y
                if idx >= 0:
                    mask[:idx+1, y] = 1
        elif choice == 2:
            direction = 'South'
            for x in range(mask.shape[0]):
                if x <= pos[0]:
                    idx = pos[0] + pos[1] - x
                else:
                    idx = x + pos[1] - pos[0]
                mask[x, idx:] = 1
        elif choice == 3:
            direction = 'North'
            for x in range(mask.shape[0]):
                if x <= pos[0]:
                    idx = x + pos[1] - pos[0]
                else:
                    idx = pos[0] + pos[1] - x
                if idx >= 0:
                    mask[x, :idx+1] = 1
        elif choice == 4:
            direction = 'South-East'
            mask[pos[0]:, pos[1]:] = 1
        elif choice == 5:
            direction = 'South-West'
            mask[:pos[0]+1, pos[1]:] = 1
        elif choice == 6:
            # North-East
            direction = 'North-East'
            mask[pos[0]:, :pos[1]+1] = 1
        elif choice == 7:
            # North-West
            direction = 'North-West'
            mask[:pos[0]+1, :pos[1]+1] = 1

        truth = self.map.check_direction(direction)
        log = "Treasure is in the {} of the pirate's position {}".format(
            direction, pos)
        return 13, log, truth, mask

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
            # choose 2 top_left and bottom_left y coordinates for each square from 0 - width and sort ascendingly
            # the higgest and lowest y is belong to the the bigger square and the 2 left is smaller one's
            col = np.sort(np.random.choice(np.arange(self.map.width), (4,)))

            # choose 2 top_left and bottom_left x coordinates for each square from 0 - height and sort descendingly
            # the higgest and lowest x is belong to the the bigger square and the 2 left is smaller one's
            row = np.sort(np.random.choice(np.arange(self.map.height), (4,)))

            small_area = (col[2] - col[1]) * (row[2] - row[1])
            big_area = (col[3] - col[0]) * (row[3] - row[0])

            # small square's area must be as big as 10% - 30% total area of the map
            if small_area >= 0.1 * map_area and small_area < 0.3 * map_area and big_area >= 0.5 * map_area and big_area < 0.7 * map_area:
                big_square = np.array([col[0], row[0], col[3], row[3]])
                small_square = np.array([col[1], row[1], col[2], row[2]])
                break

        log = "The treasure is somewhere in the gap between 2 squares: S1 = [{}], S2 = [{}]".format(
            self.map.convert_to_string(big_square), self.map.convert_to_string(small_square))

        truth, array_of_tiles = self.map.check_square_gap(
            big_square, small_square)

        return 14, log, truth, np.array([big_square, small_square])

    def gen_15th_type(self):
        '''
        The treasure is in a region that has mountain.
        '''
        list_mountain_region = self.map.get_mountain_region()
        log = "The treasure is in one of the regions {} which have mountain".format(
            self.map.convert_to_string(list_mountain_region))
        truth, array_of_tiles = self.map.check_region(list_mountain_region)
        return 15, log, truth, list_mountain_region
