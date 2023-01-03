import os
import numpy as np


def read_input_file(file_path):
    if not os.path.exists(file_path):
        return None, None, None, None, None, None
    with open(file_path, 'r') as f:
        print('Solving map')

        # Get inputs
        # contain width and height
        map_shape = [int(item) for item in f.readline().split()]
        # defines the round number that the pirate reveal location
        reveal_turn = int(f.readline())
        # defines the round number that the pirate is free
        free_turn = int(f.readline())
        num_regions = int(f.readline())  # defines the number of regions
        treasure_pos = tuple([int(item) for item in f.readline().split()])
        map = []
        mountains = []
        prisons = []

        for _ in range(map_shape[1]):
            map.append(f.readline().replace(
                ' ', '').replace('\n', '').split(';'))

        for i in range(len(map)):
            for j in range(len(map[i])):
                temp = map[i][j]
                map[i][j] = int(temp[0])
                if len(temp) >= 2:
                    if temp[1] == 'M':
                        mountains.append((j, i))
                    elif temp[1] == 'P':
                        prisons.append((j, i))

        f.close()
        return [map_shape[0], map_shape[1], reveal_turn, free_turn, np.array(map), mountains, prisons, num_regions, treasure_pos]


def write_logs_file(output_dir='data/output/', file_name='LOG_01.txt', logs=[]):
    file_path = output_dir + file_name
    f = open(file_path, 'w')
    f.write(str(len(logs)))
    f.write('\n')
    f.write(logs[-1])

    for log in logs:
        f.write('\n')
        f.write('> ' + log)

    f.close
