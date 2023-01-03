from utils import read_input_file
# import sys
# import math


# def parse_grid(grid_string):
#     # Split string into rows
#     rows = grid_string.strip().split("\n")

#     # Split rows into cells
#     cells = [row.split() for row in rows]

#     # Convert cells to integers
#     return [[int(cell.strip("MTP")) for cell in row] for row in cells]


# def visualize_grid(grid, n):
#     # Map values to colors
#     colors = {
#         0: "\033[34m",  # blue
#         1: "\033[33m",  # yellow
#         2: "\033[31m",  # red
#         3: "\033[37m",  # brown
#         4: "\033[32m",  # green
#         5: "\033[30m",  # green
#         6: "\033[35m",  # green
#     }

#     # Initialize visualization as a list of empty strings
#     vis = ["" for i in range(n)]

#     # Iterate over rows and columns
#     for i in range(n):
#         for j in range(n):
#             # Get color for value
#             # purple for other values
#             color = colors.get(grid[i][j], "\033[35m")

#             # Append colored character to visualization
#             vis[i] += color + str(grid[i][j]) + "\033[0m"

#     # Join rows of visualization into a single string
#     return "\n".join(vis)


# # Example usage
# # Example usage
# grid_string = """
# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 1 1M 1 1 1 2 2 2 0 0 0
# 0 0 0 0 1 1M 1 1 1 2 2M 2 2 0 0 0
# 0 0 0 0 1 1 1 1 1 2 2 2 2 0 0 0
# 0 0 0 0 1 1 1 1 1 2 2 2 2M 0 0 0
# 0 0 0 0 1 1 1 1 1T 2 2 2 2 0 0 0
# 0 0 0 0 1 1 1 1 1 2 2 2 2 0 0 0
# 0 0 0 0 0 0 0 0 0 2 2 2 2 0 0 0
# 0 0 0 0 0 0 0 0 0 2 2 2M 2 0 0 0
# 0 0 0 0 0 0 0 0 0 2 2 2 2M 0 0 0
# 0 0 0 0 0 3 3M 3 3 3 4 4 4 0 0 0
# 0 0 0 0 3 3 3 3 3 4 4 4 4 0 0 0
# 0 0 0 0 3 3 3 3 3 4 4 4 4 0 0 0
# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
# """

# grid = parse_grid(grid_string)

# print(visualize_grid(grid, 16))


# nd = 8
# N = 4
# n = int(math.sqrt(N))
# length = nd / n
# c = [int(i*length+length/2) for i in range(n)]

# print ([[(x,y) for x in c] for y in c])

# for i in c:
#     for j in c:
#         print(i,j)

# print(c)
# Loop over the regions
# for region in range(r):
#     # Calculate the top left coordinates of the region
#     region_x = region % r * region_side_length
#     region_y = region // r * region_side_length

#     # Calculate the center coordinates of the region
#     x = region_x + region_side_length // 2 + 1
#     y = region_y + (region_side_length // 2) * (region % 2) + 1
#     print(f"Region {region}: ({x}, {y})")


file_path = 'data/input/MAP_01.txt'
data = read_input_file(file_path)
print(data)
