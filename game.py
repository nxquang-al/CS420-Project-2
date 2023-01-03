from map import Map
from agent import Agent, cal_manhattan_distance
from pirate import Pirate
from hint import HintManager
import random
import numpy as np
from queue import Queue


class Game:
    def __init__(self, input_data):
        self.WIDTH = input_data[0]
        self.HEIGHT = input_data[1]
        if len(input_data) <= 2:
            print('Generate')
            self.map_manager = Map(self.WIDTH, self.HEIGHT, data=None)
            self.prison_revealTurn = random.randint(2, 4)
            # To ensure prirate is free after prison's position is revealed
            self.pirate_freeTurn = int(self.prison_revealTurn+0.2*self.WIDTH)
        else:
            self.prison_revealTurn = input_data[2]
            self.pirate_freeTurn = input_data[3]
            self.map_manager = Map(
                self.WIDTH, self.HEIGHT, data=input_data[4:])

        self.hint_manager = HintManager(self.map_manager)
        self.truth_list = []

        self.pirate = Pirate(map=self.map_manager,
                             treasure_pos=self.map_manager.treasure_pos)

        self.agent_pos = self.map_manager.gen_agent_pos()
        self.agent = Agent(game_manager=self, initial_pos=self.agent_pos)
        self.known_treasure = False

        # self.pirate_freeTurn = 2
        self.pirate_prev_pos = None

        # To be passed into LogDisplay of visualization.py
        self.logs = Queue()

        self.full_logs = []             # For output.txt
        self.hint_tiles = Queue()

        self.scan_area = []

        self.hint_weights = np.array(
            [1, 1, 1, 1, 1, 0, 0.5, 1, 1, 1, 1, 0.5, 0, 0.5, 1])

        self.turn_idx = 0
        self.can_tele = True
        self.pirate_isFree = False
        self.is_win = False
        self.is_lose = False

    def is_movable(self, pos):
        return self.map_manager.is_movable(pos)

    def scan_rectangle(self, top_left, bot_right):
        return self.map_manager.check_rectangle_region(top_left, bot_right)

    def get_agent_pos(self):
        return self.agent.cur_pos

    def get_pirate_pos(self):
        return self.pirate.cur_pos, self.turn_idx >= self.pirate_freeTurn

    def log_init(self):
        self.logs.put('Game start')
        self.logs.put('Agent appears at {}'.format(self.agent_pos))
        self.logs.put('The pirate\'s will be revealed at the beginning of turn {}'.format(
            self.prison_revealTurn))
        self.logs.put('The pirate will be free at the beginning of turn {}'.format(
            self.pirate_freeTurn))
        pass

    def log(self):
        '''
            Logging
        '''
        log_content = ""
        while not self.logs.empty():
            log = self.logs.get()
            log_content += f"> {log}\n"
            self.full_logs.append(log)

        return log_content  # String

    def pass_hint_tiles(self):
        hint_tiles = []
        while not self.hint_tiles.empty():
            hint_tiles.append(self.hint_tiles.get())

        return hint_tiles

    def gen_scan_area(self, scan_type):
        (x, y) = self.agent.cur_pos
        if scan_type == 1:
            self.scan_area = [(i, j) for i in range(x-1, x+2)
                              for j in range(y-1, y+2)]
        else:
            self.scan_area = [(i, j) for i in range(x-2, x+3)
                              for j in range(y-2, y+3)]

    def get_kb(self):
        return self.agent.get_kb()

    def pass_scan_area(self):
        return self.scan_area

    def visualize(self):
        return

    def get_hint_truth(self, hint_idx):
        return self.truth_list[hint_idx]

    def next_turn(self):
        # Init pirate pos here because it must be after the init of map (and prison)
        if self.pirate.cur_pos is None:
            self.pirate.set_pos(self.map_manager.prisons[random.randint(
                0, self.map_manager.num_prisons - 1)])
            self.pirate_prev_pos = self.pirate.cur_pos

        if not self.is_win and not self.is_lose:
            self.turn_idx += 1
            self.logs.put('START TURN {}'.format(self.turn_idx))

            if self.turn_idx == self.prison_revealTurn:
                self.logs.put(
                    "The Pirate is at the prison {}".format(self.pirate.cur_pos))
                self.hint_weights = np.array(
                    [1, 1, 1, 1, 1, 0, 0.5, 1, 1, 1, 1, 0.5, 1, 0.5, 1])

            if self.turn_idx == self.pirate_freeTurn:
                self.logs.put("The pirate is free")
                self.hint_weights = np.array(
                    [1, 1, 1, 1, 1, 1, 0.5, 1, 1, 1, 1, 0.5, 1, 0.5, 1])
                self.pirate_isFree = True
                self.pirate.find_shortest_path()

            if self.turn_idx == 1:
                hint_type, log, truth, data = self.hint_manager.gen_first_hint(
                    self.agent.cur_pos, self.pirate.cur_pos, self.hint_weights)
            else:
                hint_type, log, truth, data = self.hint_manager.generate(
                    self.agent.cur_pos, self.pirate.cur_pos, self.hint_weights)
            self.truth_list.append(truth)
            array_of_tiles, binary_mask = self.agent.refactor_hint(
                hint_type, data)

            if array_of_tiles is not None:
                self.hint_tiles.put(array_of_tiles)

            self.agent.add_hint(self.turn_idx, hint_type, binary_mask)

            self.logs.put('HINT {}: {}'.format(self.turn_idx, log))
            self.logs.put(f"ADD HINT {self.turn_idx} TO HINT LIST")
            if self.turn_idx == 1:
                self.logs.put('HINT 1: is_verified = TRUE, is_truth = TRUE')
                mask = self.agent.hints[0][2]
                self.agent.verify(0, True, mask)

            if self.turn_idx >= self.pirate_freeTurn:
                self.pirate_prev_pos = self.pirate.cur_pos
                if not self.pirate.path.empty():
                    (move, log) = self.pirate.path.get()
                    self.logs.put(log)
                    self.pirate.set_pos(move.tolist() if isinstance(
                        move, np.ndarray) else list(move))

            if not self.is_win and self.pirate.reach_treasure():
                self.logs.put('LOSE')
                self.is_lose = True

            step = 0
            while step < 2 and not self.is_win and not self.is_lose:
                if self.known_treasure:
                    # if tele is still available, agent tele to the treasure and takes a large scan
                    if self.can_tele:
                        self.can_tele = False
                        self.agent.teleport(self.map_manager.treasure_pos)
                        self.logs.put(
                            'Agent teleport to position: {}'.format(self.agent.cur_pos))
                        self.logs.put(
                            'Agent takes a large scan at {}'.format(self.agent.cur_pos))
                        self.is_win = True

                    # if there is no tile in path, agent arrives the target, just takes a large scan and return true
                    if len(self.agent.path) == 0 and not self.is_win:
                        self.logs.put(
                            'Agent takes a large scan at {}'.format(self.agent.cur_pos))
                        self.is_win = True

                    # Else, agent move the next step to the treasure
                    next_pos = self.agent.path.pop(0)
                    if cal_manhattan_distance(self.agent.cur_pos, next_pos) <= 2:
                        # Small move
                        self.logs.put(
                            'Agent moves from {} to tile {} and takes a small scan'.format(self.agent.cur_pos, next_pos))
                        self.agent.update_pos(next_pos)
                        self.is_win = self.agent.small_scan()
                    else:
                        # Large move
                        self.logs.put(
                            f"Agent moves from {self.agent.cur_pos} to tile {next_pos}")
                        self.agent.update_pos(next_pos)
                    step += 1

                else:
                    # Treasure position is unknown
                    # Get action of the turn
                    next_action = self.agent.get_action(
                        self.pirate_isFree, self.can_tele, self.pirate.cur_pos, self.pirate_prev_pos)
                    if next_action[1] == 0:
                        # Verification
                        (idx, turn, mask) = next_action[2]
                        truth = self.truth_list[turn-1]
                        self.agent.verify(idx, truth, mask)
                        self.logs.put(
                            f"Agent has verified the hint {turn}, it is {truth}!!")
                        step += 1
                        self.logs.put(
                            'HINT {}: is_verified = TRUE, is_truth = {}'.format(turn, truth))

                    elif next_action[1] == 1:
                        # Move 1-2 tiles and small scan
                        next_move = next_action[2]
                        prev_pos = self.agent.cur_pos[:]
                        self.agent.move(next_move)
                        self.logs.put('Agent moves a small steps from {} to {} and takes a small scan'.format(
                            prev_pos, self.agent.cur_pos))
                        has_treasure = self.agent.small_scan()
                        if has_treasure:
                            self.logs.put('WIN')
                            self.is_win = True
                        step += 1

                    elif next_action[1] == 2:
                        # Move 3-4 tiles
                        next_move = next_action[2]
                        prev_pos = self.agent.cur_pos
                        self.agent.move(next_move)
                        self.logs.put('Agent moves a large steps from {} to {}'.format(
                            prev_pos, self.agent.cur_pos))
                        step += 1

                    elif next_action[1] == 3:
                        # Large scan 5x5
                        has_treasure = self.agent.large_scan()
                        self.logs.put('Agent takes a large scan')
                        if has_treasure:
                            self.logs.put('WIN')
                            self.is_win = True
                        step += 1

                    elif next_action[1] == 4:
                        # Teleport
                        pos = next_action[2]
                        self.agent.teleport(pos)
                        self.can_tele = False
                        self.logs.put(
                            "Agent teleports to tiles {}".format(pos))
                        # this action is not counted as a step

                    if np.count_nonzero(self.agent.knowledge_map) == 1:
                        # If there is only 1 tile available, it's the treasure
                        self.known_treasure = True
                        self.agent.bfs_fastest_path()
                        # pop the current position of agent
                        self.agent.path.pop(0)
