from map import Map
from agent import Agent, cal_manhattan_distance
from pirate import Pirate
from hint import HintManager
import random
import numpy as np
from queue import Queue


class Game:
    def __init__(self, WIDTH, HEIGHT):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.map_manager = Map(self.WIDTH, self.HEIGHT)
        self.hint_manager = HintManager(self.map_manager)
        self.truth_list = []
        self.pirate = Pirate(map=self.map_manager, treasure_pos=self.map_manager.treasure_pos)

        agent_pos = (random.randint(0, self.WIDTH-4),
                     random.randint(0, self.HEIGHT-4))
        self.agent = Agent(game_manager=self, initial_pos=agent_pos)
        self.known_treasure = False

        self.prison_revealTurn = random.randint(2, 4)
        # To ensure prirate is free after prison's position is revealed
        self.pirate_freeTurn = int(4+0.2*self.WIDTH)
        self.pirate_prev_pos = None

        self.logs = Queue(maxsize=5)    # To be passed into LogDisplay of visualization.py
        self.full_logs = []             # For output.txt

        self.hint_weights = np.array(
            [1, 1, 1, 1, 1, 1, 0.5, 1, 1, 1, 1, 0.5, 1, 0.5, 1])
        
        self.turn_idx = 0
        self.can_tele = True
        self.pirate_isFree = False
        self.is_win = False
        # self.logs.append('Game start')
        # self.logs.append('Agent appears at {}}'.format(self.agent_pos))
        # self.logs.append('The pirate\'s will be revealed at the beginning of turn {}'.format(
        #     self.prison_revealTurn))
        # self.logs.append('The pirate will be free at the beginning of turn {}'.format(
        #     self.pirate_freeTurn))

    def is_movable(self, pos):
        return self.map_manager.is_movable(pos)

    def scan_rectangle(self, top_left, bot_right):
        return self.map_manager.check_rectangle_region(top_left, bot_right)

    def get_agent_pos(self):
        
        return self.agent.cur_pos

    def log_init(self):
        self.logs.put('Game start')
        self.logs.put('Agent appears at {}}'.format(self.agent_pos))
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
            
        return log_content # String

    def visualize(self):
        return

    def generate_turn(self, turn_idx):
        self.logs.put('START TURN {}'.format(turn_idx))
        if turn_idx == 1:
            hint_type, log, truth, data = self.hint_manager.gen_first_hint()
        else:
            hint_type, log, truth, data = self.hint_manager.generate()
        self.truth_list.append(truth)
        self.agent.add_hint(turn_idx, hint_type, data)

        self.logs.put('HINT {}: {}'.format(turn_idx, log))
        self.logs.put(f"ADD HINT {self.turn_idx} TO HINT LIST")
        if turn_idx == 1:
            self.logs.put('HINT 1: is_verified = TRUE, is_truth = TRUE')

    def get_hint_truth(self, hint_idx):
        return self.truth_list[hint_idx]
    
    def next_turn(self):
        # Init pirate pos here because it must be after the init of map (and prison)
        if self.pirate.cur_pos is None:
            self.pirate.set_pos(self.map_manager.prisons[random.randint(0, self.map_manager.num_prisons - 1)])

        if not self.is_win:
            self.turn_idx += 1
            self.logs.put('START TURN {}'.format(self.turn_idx))

            if self.turn_idx == self.prison_revealTurn:
                self.logs.put(
                    "The location of pirate is {}".format(self.pirate.cur_pos))

            if self.turn_idx == self.pirate_freeTurn:
                self.logs.put("The pirate has been freed")
                self.pirate_isFree = True

            if self.turn_idx == 1:
                hint_type, log, truth, data = self.hint_manager.gen_first_hint(
                    self.agent.cur_pos, self.pirate.cur_pos, self.hint_weights)
            else:
                hint_type, log, truth, data = self.hint_manager.generate(
                    self.agent.cur_pos, self.pirate.cur_pos, self.hint_weights)
            self.truth_list.append(truth)
            self.agent.add_hint(self.turn_idx, hint_type, data)

            self.logs.put('HINT {}: {}'.format(self.turn_idx, log))
            self.logs.put(f"ADD HINT {self.turn_idx} TO HINT LIST")
            if self.turn_idx == 1:
                self.logs.put('HINT 1: is_verified = TRUE, is_truth = TRUE')
                _, _, mask = self.agent.refactor_hint_data(0)
                self.agent.verify(0, True, mask)

            step = 0
            while step < 2 and not self.is_win:
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
                            'Agent moves from {self.agent.cur_pos} to tile {next_pos} and takes a small scan')
                        self.agent.update_pos(next_pos)
                        self.is_win = self.agent.small_scan()
                    else:
                        # Large move
                        self.logs.put(
                            'Agent moves from {self.agent.cur_pos} to tile {new_pos}')
                        self.agent.update_pos(next_pos)
                    step += 1

                else:
                    # Treasure position is unknown
                    # Get action of the turn
                    next_action = self.agent.get_action(self.pirate_isFree, self.can_tele,
                                                        self.pirate.cur_pos, self.pirate_prev_pos)
                    if next_action[1] == 0:
                        # Verification
                        (idx, turn, _, mask) = next_action[2]
                        truth = self.truth_list[turn-1]
                        self.agent.verify(idx, truth, mask)
                        step += 1

                    elif next_action[1] == 1:
                        # Move 1-2 tiles and small scan
                        move = next_action[2]
                        self.agent.move(move)
                        has_treasure = self.agent.small_scan()
                        if has_treasure:
                            self.logs.put('WIN')
                            self.is_win = True
                        step += 1

                    elif next_action[1] == 2:
                        # Move 3-4 tiles
                        move = next_action[2]
                        self.agent.move(move)
                        step += 1

                    elif next_action[1] == 3:
                        # Large scan 5x5
                        has_treasure = self.agent.large_scan()
                        if has_treasure:
                            self.logs.put('WIN')
                            self.is_win = True
                        step += 1

                    elif next_action[1] == 4:
                        # Teleport
                        pos = next_action[2]
                        self.agent.teleport(pos)
                        self.can_tele = False
                        # this action is not counted as a step

                    if np.count_nonzero(self.agent.knowledge_map) == 1:
                        # If there is only 1 tile available, it's the treasure
                        self.known_treasure = True
                        self.agent.bfs_fastest_path()
                        # pop the current position of agent
                        self.agent.path.pop(0)

            if self.turn_idx >= self.pirate_freeTurn:
                self.pirate_prev_pos = self.pirate.cur_pos
                (move, log) = self.pirate.path.get()
                self.logs.put(log)

            if self.pirate.reach_treasure():
                self.logs.put('LOSE')

    def run(self):
        # self.turn_idx = 0
        # self.can_tele = True
        # self.pirate_isFree = False

        # known_treasure = False
        # pirate_prev_pos = None

        # self.next_turn()
        pass

        # hint_weights = np.array(
        #     [1, 1, 1, 1, 1, 1, 0.5, 1, 1, 1, 1, 0.5, 1, 0.5, 1])
        # while True:
        #     self.turn_idx += 1
        #     self.logs.append('START TURN {}'.format(self.turn_idx))

        #     if self.turn_idx == self.prison_revealTurn:
        #         self.logs.append(
        #             "The location of pirate is {}".format(self.pirate.cur_pos))

        #     if self.turn_idx == self.pirate_freeTurn:
        #         self.logs.append("The pirate has been freed")
        #         self.pirate_isFree = True

        #     if self.turn_idx == 1:
        #         hint_type, log, truth, data = self.hint_manager.gen_first_hint(
        #             self.agent.cur_pos, self.pirate.cur_pos, hint_weights)
        #     else:
        #         hint_type, log, truth, data = self.hint_manager.generate(
        #             self.agent.cur_pos, self.pirate.cur_pos, hint_weights)
        #     self.truth_list.append(truth)
        #     self.agent.add_hint(self.turn_idx, hint_type, data)

        #     self.logs.append('HINT {}: {}'.format(self.turn_idx, log))
        #     self.logs.append('ADD HINT {turn_idx} TO HINT LIST')
        #     if self.turn_idx == 1:
        #         self.logs.append('HINT 1: is_verified = TRUE, is_truth = TRUE')
        #         _, _, mask = self.agent.refactor_hint_data(0)
        #         self.agent.verify(0, True, mask)

        #     step = 0
        #     is_win = False
        #     while step < 2 and not is_win:
        #         if known_treasure:
        #             # if tele is still available, agent tele to the treasure and takes a large scan
        #             if self.can_tele:
        #                 self.can_tele = False
        #                 self.agent.teleport(self.map_manager.treasure_pos)
        #                 self.logs.append(
        #                     'Agent teleport to position: {}'.format(self.agent.cur_pos))
        #                 self.logs.append(
        #                     'Agent takes a large scan at {}'.format(self.agent.cur_pos))
        #                 is_win = True
        #                 break

        #             # if there is no tile in path, agent arrives the target, just takes a large scan and return true
        #             if len(self.agent.path) == 0 and not is_win:
        #                 self.logs.append(
        #                     'Agent takes a large scan at {}'.format(self.agent.cur_pos))
        #                 is_win = True
        #                 break

        #             # Else, agent move the next step to the treasure
        #             next_pos = self.agent.path.pop(0)
        #             if cal_manhattan_distance(self.agent.cur_pos, next_pos) <= 2:
        #                 # Small move
        #                 self.logs.append(
        #                     'Agent moves from {self.agent.cur_pos} to tile {next_pos} and takes a small scan')
        #                 self.agent.update_pos(next_pos)
        #                 is_win = self.agent.small_scan()
        #             else:
        #                 # Large move
        #                 self.logs.append(
        #                     'Agent moves from {self.agent.cur_pos} to tile {new_pos}')
        #                 self.agent.update_pos(next_pos)
        #             step += 1

        #         else:
        #             # Treasure position is unknown
        #             # Get action of the turn
        #             next_action = self.agent.get_action(self.pirate_isFree, self.can_tele,
        #                                                 self.pirate.cur_pos, pirate_prev_pos)
        #             if next_action[1] == 0:
        #                 # Verification
        #                 (idx, turn, _, mask) = next_action[2]
        #                 truth = self.truth_list[turn]
        #                 self.agent.verify(idx, truth, mask)
        #                 step += 1

        #             elif next_action[1] == 1:
        #                 # Move 1-2 tiles and small scan
        #                 move = next_action[2]
        #                 self.agent.move(move)
        #                 has_treasure = self.agent.small_scan()
        #                 if has_treasure:
        #                     self.logs.append('WIN')
        #                     is_win = True
        #                     break
        #                 step += 1

        #             elif next_action[1] == 2:
        #                 # Move 3-4 tiles
        #                 move = next_action[2]
        #                 self.agent.move(move)
        #                 step += 1

        #             elif next_action[1] == 3:
        #                 # Large scan 5x5
        #                 has_treasure = self.agent.large_scan()
        #                 if has_treasure:
        #                     self.logs.append('WIN')
        #                     is_win = True
        #                     break
        #                 step += 1

        #             elif next_action[1] == 4:
        #                 # Teleport
        #                 pos = next_action[2]
        #                 self.agent.teleport(pos)
        #                 self.can_tele = False
        #                 # this action is not counted as a step

        #             if np.count_nonzero(self.agent.knowledge_map) == 1:
        #                 # If there is only 1 tile available, it's the treasure
        #                 known_treasure = True
        #                 self.agent.bfs_fastest_path()
        #                 # pop the current position of agent
        #                 self.agent.path.pop(0)

        #     if self.turn_idx >= self.pirate_freeTurn:
        #         pirate_prev_pos = self.pirate.cur_pos
        #         (move, log) = self.pirate.path.get()
        #         self.logs.append(log)

        #     if self.pirate.reach_treasure():
        #         self.logs.append('LOSE')
        #         break


# if known_treasure:
            #     is_win = False
            #     if self.can_tele:
            #         # if tele is still available, agent tele to the treasure and takes a large scan
            #         self.can_tele = False
            #         self.agent.teleport(self.map_manager.treasure_pos)
            #         self.logs.append(
            #             'Agent teleport to position: {}'.format(self.agent.cur_pos))
            #         is_win = self.agent.large_scan()
            #         self.logs.append(
            #             'Agent takes a large scan at {}'.format(self.agent.cur_pos))

            #     step = 0
            #     while step < 2 and not is_win and len(self.agent.path):
            #         next_pos = self.agent.path.pop(0)
            #         if cal_manhattan_distance(self.agent.cur_pos, next_pos) <= 2:
            #             # Small move
            #             self.logs.append(
            #                 'Agent moves from {self.agent.cur_pos} to tile {next_pos} and takes a small scan')
            #             self.agent.update_pos(next_pos)
            #             is_win = self.agent.small_scan()
            #         else:
            #             # Large move
            #             self.logs.append(
            #                 'Agent moves from {self.agent.cur_pos} to tile {new_pos}')
            #             self.agent.update_pos(next_pos)
            #         step += 1
            #     if len(self.agent.path) == 0 and not is_win and step < 2:
            #         self.logs.append(
            #             'Agent takes a large scan at {}'.format(self.agent.cur_pos))
            #         is_win = True
            #     if is_win:
            #         self.logs.append('WIN')
            #         break
            # else:
            #     step = 0
            #     is_win = False
            #     while step < 2 and not is_win:
            #         # Get action of the turn
            #         next_action = self.agent.get_action(self.pirate_isFree, self.can_tele,
            #                                             self.pirate.cur_pos, pirate_prev_pos)
            #         if next_action[1] == 0:
            #             # Verification
            #             (idx, turn, _, mask) = next_action[2]
            #             truth = self.truth_list[turn]
            #             self.agent.verify(idx, truth, mask)

            #         elif next_action[1] == 1:
            #             # Move 1-2 tiles and small scan
            #             move = next_action[2]
            #             self.agent.move(move)
            #             has_treasure = self.agent.small_scan()
            #             if has_treasure:
            #                 self.logs.append('WIN')
            #                 is_win = True
            #                 break

            #         elif next_action[1] == 2:
            #             # Move 3-4 tiles
            #             move = next_action[2]
            #             self.agent.move(move)

            #         elif next_action[1] == 3:
            #             # Large scan 5x5
            #             has_treasure = self.agent.large_scan()
            #             if has_treasure:
            #                 self.logs.append('WIN')
            #                 is_win = True
            #                 break

            #         elif next_action[1] == 4:
            #             # Teleport
            #             pos = next_action[2]
            #             self.agent.teleport(pos)
            #             self.can_tele = False
            #             continue    # this action is not counted as a step

            #         step += 1

            #         if np.count_nonzero(self.agent.knowledge_map) == 1:
            #             # If there is only 1 tile available, it's the treasure
            #             known_treasure = True
            #             self.agent.bfs_fastest_path()
            #             # pop the current position of agent
            #             self.agent.path.pop(0)
