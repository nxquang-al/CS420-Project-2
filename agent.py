import numpy as np
from queue import Queue
from game import Game
from scipy.sparse import coo_matrix
import heapq

class Agent:
    def __init__(self, game_manager: Game, initial_pos: tuple):
        self.game_manager = game_manager
        self.map_manager = game_manager.map_manager
        self.knowledge_map = np.empty((game_manager.width, game_manager.height))
        self.cur_pos = initial_pos
        self.hints = Queue()

        self.width = self.game_manager.width
        self.height = self.game_manager.height

        return

    def initalize(self):
        return

    def next_action(self):
        return

    def teleport(self, pos):
        if not self.game_manager.is_movable(pos):
            return False
        self.cur_pos = pos
        return True
    
    def move(self, steps, direction):
        if direction == 0:
            # East:
            new_pos = (self.cur_pos[0]+steps, self.cur_pos[1])
            if not self.game_manager.is_movable(new_pos):
                return False
            self.cur_pos = new_pos
        elif direction == 1:
            #West
            new_pos = (self.cur_pos[0]-steps, self.cur_pos[1])
            if not self.game_manager.is_movable(new_pos):
                return False
            self.cur_pos = new_pos
        elif direction == 2:
            #South
            new_pos = (self.cur_pos[0], self.cur_pos[1] + steps)
            if not self.game_manager.is_movable(new_pos):
                return False
            self.cur_pos = new_pos
        else:
            new_pos = (self.cur_pos[0], self.cur_pos[1] - steps)
            if not self.game_manager.is_movable(new_pos):
                return False
            self.cur_pos = new_pos
        return True

    def small_scan(self) -> bool:
        '''
        Take small scan, size 3x3
        '''
        top_left = (self.cur_pos[0]-1, self.cur_pos[1]-1)
        bot_right = (self.cur_pos[0]+1, self.cur_pos[1]+1)
        return self.game_manager.scan_rectangle(top_left, bot_right)

    def large_scan(self) -> bool:
        '''
        Take large scan, size 5x5
        '''
        top_left = (self.cur_pos[0]-2, self.cur_pos[1]-2)
        bot_right = (self.cur_pos[0]+2, self.cur_pos[1]+2)
        return self.game_manager.scan_rectangle(top_left, bot_right)
    
    def add_hint(self, idx, hint_type, data):
        '''
        Add index, type, and data of hint to queue
        '''
        self.hints.put((idx, hint_type, data))

    def verify(self):
        if self.hints.empty():
            return False

        hint = self.hints.get()
        self.mask = np.zeros((self.width, self.height))
        if hint[1] == 1:
            # Hint type 1, data is an array of tiles
            binary_mask = arrayTiles_to_binaryMask(hint[2])

        elif hint[1] in [2,15]:
            # Hint type 2 and 15, data is list of regions
            binary_mask = self.game_manager.get_region_tiles(hint[2])
        
        elif hint[1] == 3:
            # Hint type 3, data is list regions, which do not contain treasure
            binary_mask = np.logical_not(self.game_manager.get_region_tiles(hint[2]))

        elif hint[1] in [4,5,12]:
            # Hint type 4/5/12, data is a rectangle noted by top_left and bot_right
            top_left, bot_right = hint[2]
            binary_mask = np.zeros((self.width, self.height), dtype=bool)
            binary_mask[top_left[0]:bot_right[0], top_left[1]:bot_right[1]] = True

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
            bound_1, bound_2 = self.game_manager.get_two_regions_boundary(rid_1, rid_2)
            boundary = np.concatenate((bound_1, bound_2), axis=0)
            binary_mask = arrayTiles_to_binaryMask(boundary)
        
        elif hint[1] == 10:
            # Hint type 10, data is None
            _, binary_mask = self.game_manager.get_all_boundaries()
        
        elif hint[1] == 11:
            # Hint type 11, data is a binary map represents tiles with distance from sea
            binary_mask = hint[2]

        elif hint[1] == 13:
            binary_mask = hint[2]

        elif hint[1] == 14:
            outer_rec, inner_rec = hint[2]
            col_0, row_0, col_1, row_1 = outer_rec
            col_2, row_2, col_3, row_3 = inner_rec
            binary_mask = self.zeros((self.width, self.height), dtype=bool)
            binary_mask[col_0:col_1, row_0:row_1] = True       # outer
            binary_mask[col_2:col_3, row_2:row_3] = False      # inner

        truth = self.game_manager.get_hint_truth(hint[0])
        if truth:
            self.update_knowledge(binary_mask)
        else:
            self.update_knowledge(np.logical_not(binary_mask))

        return True

    def cal_heuristic(self, pos, size=3):
        if size == 3:
            col_0, row_0 = max(pos[0]-1,0), max(pos[1]-1,0)
            col_1, row_1 = min(pos[0]+1, self.width-1), min(pos[1]+1, self.height)
        else:
            col_0, row_0 = max(pos[0]-2,0), max(pos[1]-2,0)
            col_1, row_1 = min(pos[0]+2, self.width-1), min(pos[1]+2, self.height)
        region = self.knowledge_map[col_0:col_1, row_0:row_1]
        h = np.count_nonzero(region)
        return h
    
    def cal_dist_to_mean(self, pos, knowledge_map):
        col,row = np.where(knowledge_map==1)
        count = col.shape[0]
        sum_col = np.sum(col, axis=0)
        sum_row = np.sum(row, axis=0)
        return cal_manhattan_distance(pos, (sum_col/count, sum_row/count))

    def update_knowledge(self, mask):
        assert mask.shape == self.knowledge_map.shape
        self.knowledge_map *= self.mask
        return self.knowledge_map

    def get_best_action(self, knowledge):
        self.verify()

        best_move = None
        best_score = -9999999
        action = 1
        movable = np.ones(4, dtype=bool)

        # Estimate stay & 5x5 scan
        dist_2_mean = self.cal_dist_to_mean(self.cur_pos, knowledge)
        heuristic = self.cal_heuristic(self.cur_pos, size=5)
        if best_score < heuristic - dist_2_mean:
            best_score = heuristic - dist_2_mean
            best_move = (0,0)
            action = 3

        # Estimate small move & 3x3 scan
        for i,move in enumerate([(1,0), (-1,0), (0,1), (0,-1), (2,0), (-2,0), (0,2), (0,-2)]):
            x = self.cur_pos[0] + move[0]
            y = self.cur_pos[1] + move[1]
            if x < 0 or x >= self.width or movable[i%4] == False:
                continue
            if self.map_manager.is_sea((x,y)) or self.map_manager.is_mountain((x,y)):
                movable[i%4] = False
                continue

            dist_2_mean = self.cal_dist_to_mean((x,y), knowledge)
            heuristic = self.cal_heuristic((x, y), size=3)
            if best_score < heuristic - dist_2_mean:
                best_score = heuristic - dist_2_mean
                best_move = move
                action = 1

        # Estimate large move without scan
        for move in [(3,0), (-3,0), (0,3), (0,-3), (4,0), (-4,0), (0,4), (0,-4)]:
            x = self.cur_pos[0] + move[0]
            y = self.cur_pos[1] + move[1]
            if x < 0 or x >= self.width or movable[i%4] == False:
                continue
            if self.map_manager.is_sea((x,y)) or self.map_manager.is_mountain((x,y)):
                movable[i%4] = False
                continue
            dist_2_mean = self.cal_dist_to_mean((x,y), knowledge)
            if best_score < -dist_2_mean:
                best_score = -dist_2_mean
                best_move = move
                action = 2
        
        return action, best_move
        
        
    
    def phase_2_action(self, pirate_cur_pos, pirate_prev_pos):
        x = pirate_cur_pos[0] - pirate_prev_pos[0]
        y = pirate_cur_pos[1] - pirate_prev_pos[1]
        
        knowledge_clone = np.copy(self.knowledge_map)
        if y==0 and x in [1,2]:
            # Pirate moved right
            knowledge_clone[:pirate_cur_pos[0],] = 0
        
        elif y==0 and x in [-1,-2]:
            # Pirate moved left
            knowledge_clone [(pirate_cur_pos[0]+1):,] = 0
        
        elif x==0 and y in [1,2]:
            # Pirate moved down
            knowledge_clone[:, :pirate_cur_pos[1]] = 0
        
        elif x==0 and y in [-1,-2]:
            # Pirate moved up
            knowledge_clone[:, (pirate_cur_pos[1]+1):] = 0
        
        elif x==1 and y==1:
            # Pirate moved down right
            knowledge_clone[:pirate_cur_pos[0],] = 0
            knowledge_clone[:, :pirate_cur_pos[1]] = 0
        
        elif x==1 and y==-1:
            # Pirate moved up right
            knowledge_clone[:pirate_cur_pos[0],] = 0
            knowledge_clone[:, (pirate_cur_pos[1]+1):] = 0
        
        elif x==-1 and y==1:
            # Pirate moved down left
            knowledge_clone[(pirate_cur_pos[0]+1):,] = 0
            knowledge_clone[:, :pirate_cur_pos[1]] = 0
        
        else:
            # Pirate moved up left
            knowledge_clone[(pirate_cur_pos[0]+1):, ] = 0
            knowledge_clone[:, (pirate_cur_pos[1]+1):] = 0
        
        return self.get_best_action(knowledge_clone)

    def get_actions(self, pirate_isFree: bool, can_tele: bool, pirate_cur_pos: tuple, pirate_prev_pos: tuple):
        return

            



def cal_manhattan_distance(from_pos, to_pos):
    return abs(from_pos[0] - to_pos[0]) + abs(from_pos[1] - to_pos[1])

def arrayTiles_to_binaryMask(list_indices):
    '''
    Convert list/array of tiles to a binary mask
    Return: a binary numpy array (sparse matrix)
    '''
    col, row = np.split(list_indices, 2, axis=1)
    col, row = col.flatten(), row.flatten()
    data = np.ones(col.shape[0], dtype=bool)
    
    # Use scipy.coo_matrix to create a sparse matrix
    mask = coo_matrix((data, (col, row)), shape=(16, 16)).toarray()
    return mask