def generate_map(size, num_values):
    # Create an empty map
    map = []
    for i in range(size):
        map.append([0] * size)
    
    # Assign values to the map cells
    value = 1
    for i in range(size):
        for j in range(size):
            map[i][j] = value
            if value < num_values:
                value += 1
            else:
                value = 1
    return map

# Example usage:
map = generate_map(4,4)

# for row in map:
#     print(row)
# Output: [[1, 1, 2, 2], [1, 1, 2, 3], [3, 3, 3, 3], [4, 4, 4, 4]]

import numpy as np

# # Set of possible values
# values = [0, 1, 2, 3, 4]
# possible_regions = {2, 4, 5}

# # Number of elements in the set
# n = len(values)

# # Probabilities for each element in the set
# probs = [3 / (n+2)] + [1 / (n+2)] * (n-1)

# # Normalize the probabilities to sum to 1
# # probs = probs / sum(probs)

# # Choose a single random element
# random_element = np.random.choice(values, p=probs)

# region = np.random.choice(possible_regions, p=probs)

# print(random_element)  # Output: 0
# print(region)

x, y = 0, 0


# direction = np.array([[-1, 0], [1, 0] [0, -1], [0, 1] [-1, 1], [1, 1] [1, -1], [-1, -1]])
#                 # choices = 
# branch = np.random.randint(8)
# new_x, new_y = x+branch[0], y+branch[1]

# # print(new_x, new_y)
# import numpy as np

# NumPy array
arr = np.array([[1, 2], [3, 4], [5, 6]])

# Select a random element from the array
n = len(arr)  # Number of elements in the array
index = np.random.randint(n)  # Generate a random integer between 0 and n-1
new_x, new_y = x+arr[index,0], y+arr[index,1]
print(new_x, new_y)  # Output: one of the elements from the first column of the array (1, 3, or 5)