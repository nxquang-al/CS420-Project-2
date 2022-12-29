import numpy as np
from queue import Queue
from hint import HintManager

class Pirate:
    '''
        This class manage the behavior of pirate
    '''
    def __init__(self, initial_pos):
        # A queue of cells, which is the shortest path to treasure, an element contains (pos, log) where 
        # pos is an numpy array representing the coordinate of the next move 
        # log is the log of the next move
        self.path = Queue() 
        self.visited = None # A numpy array of visited cells
        self.initial_pos = initial_pos
        self.cur_pos = initial_pos
        self.hint_manager = HintManager()

    def cal_manhattan_dist(self, next_pos):
        return abs(next_pos[0] - self.hint_manager.map.treasure_pos[0]) + abs(next_pos[1] - self.hint_manager.map.treasure_pos[1])

    def move_4_directions(self, cur_move):
        #a state would have [prev_x, prev_y, next_x, next_y, direction, num_tiles, path_cost, heuristics]
        #prev_x and prev_y: coordinate of the previous move
        #next_x, next_y: coordinate of the next move
        #direction is the way that pirate moves, it could be moving down (to the south) or moving up and then to the right (to north and then to east or di duong cheo ay)
        #direction's value: 
        #0: move to north 
        #1: move to south
        #2: move to west
        #3: move to east
        #4: move to north and then to west 
        #5: move to north and then to east
        #6: move to south and then to west
        #7: move to south and then to east
        #8: move to west and then to north
        #9: move to west and then to south
        #10: move to east and then to north
        #11: move to east and then to north
        #num_tiles: the number of tiles for the next move (1 or 2 only)
        #path_cost: total cost from beginning (at the prison) to the next tile
        #heuristics: heuristics of the next move 
        cur_pos = cur_move[2:4]
        prev_direction = cur_move[4]
        if np.array_equal(cur_pos, self.cur_pos): 
            step = 1 
            cost = cur_move[6] + 1
            prev_direction = -1
        else:
            step = 2
            cost = cur_move[6]

        offset_pos = np.array([[0, -1], [0, 1], [-1, 0], [1, 0]])
        prev_pos = np.full((4, 2), cur_pos)                
        next_pos = cur_pos + offset_pos
        if prev_direction == 0:
            directions = np.array([0, 1, 4, 5])
        elif prev_direction == 1:
            directions = np.array([0, 1, 6, 7])
        elif prev_direction == 2:
            directions = np.array([8, 9, 2, 3])
        elif prev_direction == 3:
            directions = np.array([10, 11, 2, 3])
        else:
            directions = np.array([0, 1, 2, 3])
        directions = directions.reshape((4, 1)) 
        num_tiles = np.full((4, 1), step)
        path_costs = np.full((4, 1), cost)
        heuristics = np.apply_along_axis(self.cal_manhattan_dist, 1, next_pos).reshape((4, 1))
        next_moves = np.concatenate((prev_pos, next_pos, directions, num_tiles, path_costs, heuristics), axis=1)  
            
        #submask_1 checks whether the next move of pirate is still in the map or not
        #submask_2 checks whether the next move of pirate is not to the mountain, sea or not
        #submask_3 checks whether the next move is different from the cur_pos of the pirate or not
        #mask check all conditions stated in submask_1 and submask_2
        col = next_moves[:, 2]
        row = next_moves[:, 3]
        pos = next_moves[:, 2:4]
        submask_1 = np.logical_and(np.logical_and(col >= 0, col < self.hint_manager.map.width), np.logical_and(row >= 0, row < self.hint_manager.map.height))
        submask_2 = np.logical_and(self.hint_manager.map.map[col, row] != 0, np.array([not np.any(np.equal(p, self.hint_manager.map.mountains).all(1)) for p in pos]))
        submask_3 = ~np.equal(pos, self.cur_pos).all(1)
        mask = np.logical_and(np.logical_and(submask_1, submask_2), submask_3)
        #remove all the next move of pirate that is not satisfied the above conditions 
        next_moves = next_moves[mask]
        
        return next_moves

    def get_next_moves(self, cur_move):

        #move up, down, left, right by 1 step first
        next_moves = self.move_4_directions(cur_move)
        
        #now from each tile that we have moved to, we mobe by 1 step to create 2-step moves
        for move in next_moves:
            next_2_tiles_moves = self.move_4_directions(move)
            next_moves = np.concatenate((next_moves, next_2_tiles_moves), axis=0)

        #perform sorting so that all next moves are ordered by path_cost + heuristics and then by the direction since anh Thuyen said that
        # Phụ thuộc vào đường đi ngắn nhất nhưng ưu tiên đi thẳng theo số bước lớn nhất có thể.
        ind = np.lexsort((next_moves[:, 4], next_moves[:, 6] + next_moves[:, 7]))
        next_moves = next_moves[ind]
        
        return next_moves

    def get_log(self, cur_move):
        #[prev_x, prev_y, next_x, next_y, direction, num_tiles, path_cost, heuristics]
        cur_pos = cur_move[2:4]
        direction = cur_move[4]
        num_tiles = cur_move[5]
        if direction == 0:
            log = "The pirate moves {} steps to the north.".format(num_tiles)
        elif direction == 1:
            log = "The pirate moves {} steps to the south.".format(num_tiles)
        elif direction == 2:
            log = "The pirate moves {} steps to the west.".format(num_tiles)
        elif direction == 3:
            log = "The pirate moves {} steps to the east.".format(num_tiles)
        elif direction == 4:
            log = "The pirate moves 1 step to the north and then 1 step to the west."
        elif direction == 5:
            log = "The pirate moves 1 step to the north and then 1 step to the east."
        elif direction == 6:
            log = "The pirate moves 1 step to the south and then 1 step to the west."
        elif direction == 7:
            log = "The pirate moves 1 step to the south and then 1 step to the east."
        elif direction == 8:
            log = "The pirate moves 1 step to the west and then 1 step to the north."
        elif direction == 9:
            log = "The pirate moves 1 step to the west and then 1 step to the south."
        elif direction == 10:
            log = "The pirate moves 1 step to the east and then 1 step to the north."
        elif direction == 11:
            log = "The pirate moves 1 step to the east and then 1 step to the south."
        else:
            log = "The pirate is at the {} prison. The pirate is free".format(cur_pos)
        return log

    def find_shortest_path(self):
        '''
            Find shortes path to treasure using A* search+
        '''
        initial_move = np.array([-1, -1, self.cur_pos[0], self.cur_pos[1], -1, 0, 0, self.cal_manhattan_dist(self.cur_pos)])
        
        frontier = np.array([initial_move])
        
        explored = None

        while np.size(frontier):
            #choose 1 and move and do not left anything
            cur_move = frontier[0]    
            frontier = frontier[frontier.shape[0] + 1:]   
            
            self.cur_pos = cur_move[2:4]
            log = self.get_log(cur_move)
            self.path.put((self.cur_pos, log)) 
            
            #goal test
            if np.array_equal(self.cur_pos, self.hint_manager.map.treasure_pos):
                break
            
            #add node to explored
            if explored is None:
                explored = np.array([self.cur_pos])
            else:
                explored = np.concatenate((explored, self.cur_pos[None, :]), axis=0)
            
            #get successors and remove successors which are in explored
            next_moves = self.get_next_moves(cur_move)
            mask = np.array([not np.any(np.equal(move, explored).all(1)) for move in next_moves[:, 2:4]])
            next_moves = next_moves[mask]

            #add to frontier and sort again
            frontier = np.concatenate((frontier, next_moves), axis=0)   
            ind = np.lexsort((frontier[:, 4], frontier[:, 6] + frontier[:, 7]))
            frontier = frontier[ind]

        self.cur_pos = self.initial_pos
        return

    def test_run(self):
        while not self.path.empty():
            next_move = self.path.get()
            print(next_move[0], ' --- ', next_move[1])

# 
# def main():
#     pirate = Pirate(np.array([5, 11]))
#     pirate.find_shortest_path()
#     pirate.test_run()
#     return

# if __name__ == "__main__":
#     main()