import numpy as np
from queue import Queue
from game import Game
from scipy.sparse import coo_matrix
import heapq


class Agent:
    def __init__(self, game_manager: Game, initial_pos: tuple):
        self.game_manager = game_manager
        self.map_manager = game_manager.map_manager
        self.knowledge_map = np.ones(
            (game_manager.width, game_manager.height), dtype=bool)
        self.cur_pos = initial_pos
        self.hints = []

        self.width = self.game_manager.width
        self.height = self.game_manager.height

        self.path = None

        return

    def initalize(self):
        return

    def teleport(self, pos):
        if not self.game_manager.is_movable(pos):
            return False
        self.cur_pos = pos
        return True

    def update_pos(self, pos):
        self.cur_pos = pos

    def move(self, move):
        (col, row) = move
        self.cur_pos[0] += col
        self.cur_pos[1] += row

    def small_scan(self) -> bool:
        '''
        Take small scan, size 3x3
        '''
        top_left = (max(self.cur_pos[0]-1, 0), max(self.cur_pos[1]-1, 0))
        bot_right = (min(self.cur_pos[0]+1, self.width),
                     min(self.cur_pos[1]+1, self.height))
        has_tresure = self.game_manager.scan_rectangle(top_left, bot_right)
        if has_tresure:
            return True
        self.knowledge_map[top_left[0]:(
            bot_right[0]+1), top_left[1]:(bot_right[1]+1)] = 0
        return False

    def large_scan(self) -> bool:
        '''
        Take large scan, size 5x5
        '''
        top_left = (max(self.cur_pos[0]-2, 0), max(self.cur_pos[1]-2, 0))
        bot_right = (min(self.cur_pos[0]+2, self.width),
                     min(self.cur_pos[1]+2, self.height))
        has_treasure = self.game_manager.scan_rectangle(top_left, bot_right)
        if has_treasure:
            return True
        self.knowledge_map[top_left[0]:(
            bot_right[0]+1), top_left[1]:(bot_right[1]+1)] = 0
        return False

    def add_hint(self, idx, hint_type, data):
        '''
        Add index, type, and data of hint to queue
        '''
        self.hints.append((idx, hint_type, data))

    def refactor_hint_data(self, hint_idx):
        hint = self.hints[hint_idx]
        if hint[1] == 1:
            # Hint type 1, data is an array of tiles do not contain treasure
            binary_mask = arrayTiles_to_binaryMask(hint[2], flip=True)

        elif hint[1] in [2, 15]:
            # Hint type 2 and 15, data is list of regions
            binary_mask = np.isin(self.map_manager.map, hint[2])

        elif hint[1] == 3:
            # Hint type 3, data is list regions, which do not contain treasure
            binary_mask = np.logical_not(
                np.isin(self.map_manager.map, hint[2]))

        elif hint[1] == 4:
            # Hint type 4, data is a rectangle contains treasure noted by top_left and bot_right
            binary_mask = arrayTiles_to_binaryMask(hint[2], flip=False)

        elif hint[1] == 5:
            # Hint type 5, data is a rectangle does not contain treasure
            binary_mask = arrayTiles_to_binaryMask(hint[2], flip=True)

        elif hint[1] == 7:
            # Hint type 7, data is column or/and row contain treasure
            col, row = hint[2]
            binary_mask = np.zeros((self.width, self.height), dtype=bool)
            if col:
                binary_mask[col,] = 1
            if row:
                binary_mask[:, row] = 1

        elif hint[1] == 8:
            # Hint type 8, data is column/row do not contain treasure
            col, row = hint[2]
            binary_mask = np.ones((self.width, self.height), dtype=bool)
            if col:
                binary_mask[col,] = 0
            if row:
                binary_mask[:, row] = 0

        elif hint[1] == 9:
            # Hint type 9, data is indices of 2 regions
            rid_1, rid_2 = hint[2]
            bound_1, bound_2 = self.map_manager.get_two_regions_boundary(
                rid_1, rid_2)
            boundary = np.concatenate((bound_1, bound_2), axis=0)
            binary_mask = arrayTiles_to_binaryMask(boundary, flip=False)

        elif hint[1] == 10:
            # Hint type 10, data is None
            _, binary_mask = self.map_manager.get_all_boundaries()

        elif hint[1] == 11:
            # Hint type 11, data is a binary map represents tiles with distance from sea
            binary_mask = hint[2]

        elif hint[1] == 12:
            # Hint type 12, data is a rectangle noted by top_left and bot_right
            top_left, bot_right = hint[2]
            binary_mask = np.zeros((self.width, self.height), dtype=bool)
            binary_mask[top_left[0]:bot_right[0],
                        top_left[1]:bot_right[1]] = True

        elif hint[1] == 13:
            binary_mask = hint[2]

        elif hint[1] == 14:
            outer_rec, inner_rec = hint[2]
            col_0, row_0, col_1, row_1 = outer_rec
            col_2, row_2, col_3, row_3 = inner_rec
            binary_mask = self.zeros((self.width, self.height), dtype=bool)
            binary_mask[col_0:(col_1+1), row_0:(row_1+1)] = True       # outer
            binary_mask[col_2:(col_3+1), row_2:(row_3+1)] = False      # inner

        # truth = self.game_manager.get_hint_truth(hint[0])
        # if truth:
        #     self.update_knowledge(binary_mask)
        # else:
        #     self.update_knowledge(np.logical_not(binary_mask))
        # if not truth:
        #     binary_mask = np.logical_not(binary_mask)

        # temp = np.logical_xor(binary_mask, self.knowledge_map)
        # binary_mask = np.logical_and(binary_mask, temp)
        # count = np.where(binary_mask==1)   # The number of new tiles scanned that hint can provide

        return hint[0], hint[1], binary_mask  # turn_idx, hint_type, mask

    def verify(self, index, truth, mask):
        if truth:
            self.update_knowledge(mask)
        else:
            self.update_knowledge(np.logical_not(mask))
        self.hints.pop(index)

    def update_knowledge(self, mask):
        assert mask.shape == self.knowledge_map.shape
        self.knowledge_map = np.logical_and(self.knowledge_map, mask)
        return self.knowledge_map

    def cal_heuristic(self, pos, size=3):
        if size == 3:
            col_0, row_0 = max(pos[0]-1, 0), max(pos[1]-1, 0)
            col_1, row_1 = min(pos[0]+1, self.width -
                               1), min(pos[1]+1, self.height)
        else:
            col_0, row_0 = max(pos[0]-2, 0), max(pos[1]-2, 0)
            col_1, row_1 = min(pos[0]+2, self.width -
                               1), min(pos[1]+2, self.height)
        region = self.knowledge_map[col_0:(col_1+1), row_0:(row_1+1)]
        h = np.count_nonzero(region)
        return h

    def cal_dist_to_mean(self, pos, knowledge_map):
        col, row = np.where(knowledge_map == 1)
        count = col.shape[0]
        sum_col = np.sum(col, axis=0)
        sum_row = np.sum(row, axis=0)
        return cal_manhattan_distance(pos, (sum_col/count, sum_row/count))

    def get_best_action(self, knowledge):
        actions = []
        movable = np.ones(4, dtype=bool)
        num_available = np.count_nonzero(self.knowledge_map)

        # Estimate verify action
        for i in range(len(self.hints)):
            turn, hint_type, binary_mask = self.refactor_hint_data(i)
            temp = np.logical_and(binary_mask, self.knowledge_map)
            count = np.count_nonzero(temp)
            heapq.heappush(
                actions, (count, 0, (i, turn, hint_type, binary_mask)))

        # Estimate stay & 5x5 scan
        heuristic = self.cal_heuristic(self.cur_pos, size=5)
        heapq.heappush(actions, (heuristic, 3, (0, 0)))

        # Estimate small move & 3x3 scan
        temp = 999999
        selected_move = None
        count = 0
        for i, move in enumerate([(1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)]):
            x = self.cur_pos[0] + move[0]
            y = self.cur_pos[1] + move[1]
            if x < 0 or x >= self.width or y < 0 or y >= self.height or movable[i % 4] == False:
                continue
            if self.map_manager.is_sea((x, y)) or self.map_manager.is_mountain((x, y)):
                movable[i % 4] = False
                continue

            dist_2_mean = self.cal_dist_to_mean((x, y), knowledge)
            heuristic = self.cal_heuristic((x, y), size=3)
            if temp > dist_2_mean - heuristic:
                temp = dist_2_mean - heuristic
                selected_move = move
                count = heuristic
        heapq.heappush(
            actions, (count + min(num_available+1, 6), 1, selected_move))

        # Estimate large move without scan
        selected_move = None
        for i, move in enumerate([(3, 0), (-3, 0), (0, 3), (0, -3), (4, 0), (-4, 0), (0, 4), (0, -4)]):
            x = self.cur_pos[0] + move[0]
            y = self.cur_pos[1] + move[1]
            if x < 0 or x >= self.width or y < 0 or y >= self.height or movable[i % 4] == False:
                continue
            if self.map_manager.is_sea((x, y)) or self.map_manager.is_mountain((x, y)):
                movable[i % 4] = False
                continue
            dist_2_mean = self.cal_dist_to_mean((x, y), knowledge)
            if temp > dist_2_mean:
                temp = dist_2_mean
                selected_move = move
        if selected_move:
            heapq.heappush(
                actions, (min(num_available+2, 8), 2, selected_move))

        return actions[-1]

    def phase_2_action(self, pirate_cur_pos, pirate_prev_pos):
        x = pirate_cur_pos[0] - pirate_prev_pos[0]
        y = pirate_cur_pos[1] - pirate_prev_pos[1]

        knowledge_clone = np.copy(self.knowledge_map)
        if y == 0 and x in [1, 2]:
            # Pirate moved right
            knowledge_clone[:pirate_cur_pos[0],] = 0

        elif y == 0 and x in [-1, -2]:
            # Pirate moved left
            knowledge_clone[(pirate_cur_pos[0]+1):,] = 0

        elif x == 0 and y in [1, 2]:
            # Pirate moved down
            knowledge_clone[:, :pirate_cur_pos[1]] = 0

        elif x == 0 and y in [-1, -2]:
            # Pirate moved up
            knowledge_clone[:, (pirate_cur_pos[1]+1):] = 0

        elif x == 1 and y == 1:
            # Pirate moved down right
            knowledge_clone[:pirate_cur_pos[0],] = 0
            knowledge_clone[:, :pirate_cur_pos[1]] = 0

        elif x == 1 and y == -1:
            # Pirate moved up right
            knowledge_clone[:pirate_cur_pos[0],] = 0
            knowledge_clone[:, (pirate_cur_pos[1]+1):] = 0

        elif x == -1 and y == 1:
            # Pirate moved down left
            knowledge_clone[(pirate_cur_pos[0]+1):,] = 0
            knowledge_clone[:, :pirate_cur_pos[1]] = 0

        else:
            # Pirate moved up left
            knowledge_clone[(pirate_cur_pos[0]+1):, ] = 0
            knowledge_clone[:, (pirate_cur_pos[1]+1):] = 0

        return self.get_best_action(knowledge_clone)

    def get_action(self, pirate_isFree: bool, can_tele: bool, pirate_cur_pos: tuple, pirate_prev_pos: tuple):
        if not pirate_isFree:
            # if pirate is not freed, just be greedy
            return self.get_best_action(self.knowledge_map)
        else:
            # if pirate is free at this turn, agent tele to the position of pirate
            if can_tele:
                return (0, 4, pirate_cur_pos)
            # pirate has not moved yet
            if pirate_cur_pos == pirate_prev_pos:
                # large scan
                return (0, 3, (0, 0))
            return self.phase_2_action(pirate_cur_pos, pirate_prev_pos)

    def bfs_fastest_path(self):
        paths = [[self.cur_pos]]
        visited = [self.cur_pos]

        while self.paths:
            path = self.paths.pop(0)
            if path[-1] == self.map_manager.treasure_pos:
                self.path = path
                return self.path

            movable = np.ones(4, dtype=bool)
            list_adj = np.array(
                [(-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2), (-3, 0), (3, 0), (0, -3), (0, 3), (-4, 0), (4, 0), (0, -4), (0, 4)])
            for i, move in enumerate(list_adj):
                x = path[-1][0] + move[0]
                y = path[-1][1] + move[1]
                if x < 0 or x >= self.width or y < 0 or y >= self.height:
                    continue
                if (x, y) in visited:
                    continue
                if self.map_manager.is_sea((x, y)) or self.map_manager.is_mountain((x, y)) or not movable[i % 4]:
                    movable[i % 4] = False
                    continue
                paths.append(path + [(x, y)])
                visited.append((x, y))
        return None


def cal_manhattan_distance(from_pos, to_pos):
    return abs(from_pos[0] - to_pos[0]) + abs(from_pos[1] - to_pos[1])


def arrayTiles_to_binaryMask(list_indices, flip=False):
    '''
    Convert list/array of tiles to a binary mask
    Return: a binary numpy array (sparse matrix)
    '''
    col, row = np.split(list_indices, 2, axis=1)
    col, row = col.flatten(), row.flatten()
    data = np.ones(col.shape[0], dtype=bool)

    # Use scipy.coo_matrix to create a sparse matrix
    mask = coo_matrix((data, (col, row)), shape=(16, 16)).toarray()
    if flip:
        mask = np.logical_not(mask)
    return mask
