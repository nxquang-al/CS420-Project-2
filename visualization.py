import tkinter
import customtkinter as tk
from tkinter import ttk
import sv_ttk
from map import Map
import numpy as np
import random
from queue import Queue
from game import Game

'''
    DO NOT RUN THIS FILE WITH ANACONDA ENVIRONMENT.
    IT SUCKS

    TO CHANGE THE SIZE OF MAP, SCROLL TO THE BOTTOM OF THE MAP.PY TO MODIFY "N"
'''


'''
    Define colors
'''
sea_color = "steel blue"
soil_color = "tan4"
dark_pink = "HotPink4"
sand_color = "burlywood3"
light_green = "medium sea green"
dark_green = "PaleGreen4"
light_pink = "LightPink3"
default = "CadetBlue4"

colors = {
    0: sea_color,
    1: soil_color,
    2: light_pink,
    3: light_green,
    4: dark_green,
    5: sand_color,
    6: dark_pink,
    7: default,
}

tile_colors = {
    'P': "gray90",
    'T': "gold"
}

# Set color theme (for button and stuff)
tk.set_default_color_theme("dark-blue")


# Array of hint tiles (for testing)
tiles_hint = np.array([[3, 3], [3, 4], [3, 5], [4, 3], [5, 3]])
tiles_hint2 = np.array([[7, 3], [7, 4], [7, 5], [4, 7], [5, 7]])

# Array of tiles without treasure (for testing)
tiles_no_treasure = np.array([[3, 11], [3, 12], [3, 13],
                             [4, 11], [4, 12], [4, 13],
                             [5, 11], [5, 12], [5, 13]])


class Agent:
    '''
        Agent for testing
    '''

    def __init__(self, x=2, y=2) -> None:
        self.x = x
        self.y = y

    def move_agent(self, x_des, y_des):
        tile_type_des = map.tile_type(x_des, y_des)
        width, height = map.get_map_shape()
        if (tile_type_des != 'M' and x_des > 0 and x_des < width
                and y_des > 0 and y_des < height):
            self.x = x_des
            self.y = y_des
        pass

    def get_pos(self):
        return self.x, self.y


class App(tk.CTk):
    '''
        Application, responsible for managing main grids, components
        and button onClick
    '''

    def __init__(self, game, map_cols=16, map_rows=16):
        super().__init__()

        self.map_cols = map_cols
        self.map_rows = map_rows

        self.title("Treasure Island")

        self.game = game

        # Display map
        self.map_display = MapDisplay(
            self, cols=self.map_cols, rows=self.map_rows)
        self.map_display.grid(row=0, column=0, padx=20, pady=20)

        # Display other information (Logs, regions and note)
        self.side_information = SideInformation(self)
        self.side_information.grid(row=0, column=1, padx=20, pady=20)

        # Button to show Next turn
        self.button = tk.CTkButton(self, text="Next turn", font=(
            "Roboto", 20), command=self.next_turn)
        self.button.grid(row=1, column=1, padx=10, pady=0)

        self.count = 0      # For testing

    def draw_map(self):
        self.map_display.display()  # Display map
        self.map_display.create_agent()  # Randomize init position of agent, for testing

    def draw_side_information(self):
        self.side_information.draw_log()  # Display Logs
        self.side_information.draw_region()  # Display Region labels

    # Button to move onto the next state
    def next_turn(self, log_content="", note_content=""):
        self.game.next_turn()
        # For testing
        self.count += 1
        if log_content == "":
            self.side_information.log_display.insert_log(
                f" Log content {self.count}")
            self.side_information.note_display.insert_note(
                f"Note content {self.count}")
        else:
            self.side_information.log_display.insert_log(log_content)
            self.side_information.note_display.insert_note(note_content)

        self.map_display.move_agent()

        if self.count % 2 == 0:
            self.map_display.show_hints(tiles_hint)
        else:
            self.map_display.show_hints(tiles_hint2)

        # self.map_display.display_no_treasure(tiles_no_treasure)


class SideInformation(tk.CTkFrame):
    '''
        Responsible for the half right of the window, manage Logs, Regions and Note
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.region_display = RegionDisplay(self, num_regions=map.num_regions)
        self.region_display.grid(row=0, column=0, padx=10, pady=10)

        self.log_display = LogDisplay(self)
        self.log_display.grid(row=1, column=0, padx=10, pady=10)

        self.note_display = NoteDisplay(self)
        self.note_display.grid(row=2, column=0, padx=10, pady=10)

    def draw_log(self):
        self.log_display.insert_log()

    def draw_region(self):
        self.region_display.display()

    def draw_note(self):
        self.note_display.insert_note()


class MapDisplay(tk.CTkFrame):
    def __init__(self, *args, cols=16, rows=16, map_size=832, **kwargs):
        super().__init__(*args, **kwargs)

        self.map_size = map_size
        self.cols = cols
        self.rows = rows
        self.cell_width = map_size//cols    # Width of each cell
        self.cell_height = map_size//rows

        self.cell_font_size = (
            10 if self.cols >= 64 else 14 if self.cols == 32 else 22)

        # The Ox coordinate
        self.xcoor = tk.CTkCanvas(master=self, width=self.map_size,
                                  height=self.cell_height, bg="gray13", highlightthickness=0)
        self.xcoor.grid(row=0, column=1)

        # The Oy coordinate
        self.ycoor = tk.CTkCanvas(master=self, width=self.cell_width,
                                  height=self.map_size, bg="gray13", highlightthickness=0)
        self.ycoor.grid(row=1, column=0)

        self.map = tk.CTkCanvas(
            master=self, width=self.map_size, height=self.map_size, highlightthickness=0)
        self.map.grid(row=1, column=1)

        self.agent = Agent()    # Init an agent object for testing

        # Queue for agent position, each state the old_position will be pop out.
        # The queue maintains its only element
        self.agent_pos = Queue(maxsize=2)
        self.hints = Queue(maxsize=2)

        self.rect_ids = np.empty(
            (rows, cols), dtype=int)   # ObjectID for easier
        # modification of tkinter canvas
        self.text_ids = np.empty((rows, cols), dtype=int)

    # Randomize the init position of agent FOR TESTING

    def create_agent(self):
        while True:
            height, width = map.get_map_shape()
            x_des, y_des = random.randint(
                2, width - 2), random.randint(2, height - 2)

            # Get the tipe of tile
            tile_type_des = map.tile_type(x_des, y_des)
            if (tile_type_des != "M" and tile_type_des != "P" and tile_type_des != "T"
                    and map.map[y_des, x_des] != 0):

                # Update agent's new position to the Agent object
                self.agent.move_agent(x_des, y_des)

                # Push its Canvas.TextID as its new position into the queue
                self.agent_pos.put(self.map.create_text((x_des+0.5)*self.cell_width,
                                                        (y_des+0.5) *
                                                        self.cell_height,
                                                        text='A',
                                                        anchor="center",
                                                        font=(
                                                            "Roboto bold", self.cell_font_size),
                                                        fill="orange red"))
                break

    # Randomize the position of agent FOR TESTING
<< << << < HEAD
   def move_agent(self, x_des=5, y_des=5):
        height, width = map.get_map_shape()
        while True:
            x_des, y_des = random.randint(
                2, width - 2), random.randint(2, height - 2)
            tile_type_des = map.tile_type(x_des, y_des)
            if (tile_type_des != "M" and map.map[y_des, x_des] != 0):
                self.agent.move_agent(x_des, y_des)
                self.agent_pos.put(self.map.create_text((x_des+0.5)*self.cell_width,
                                                        (y_des+0.5) *
                                                        self.cell_height,
                                                        text='A',
                                                        anchor="center",
                                                        font=(
                                                            "Roboto bold", self.cell_font_size),
                                                        fill="orange red"))
                self.map.delete(self.agent_pos.get())
                break

    # Display the hint tiles as cell with red borders.
    def show_hints(self, hint_tiles):

        # Pop out and remove the old hints (both in queue and on map display)
        if not self.hints.empty():
            old_hints = self.hints.get()
            for (i, j) in old_hints:
                self.map.tag_lower(self.rect_ids[i][j])
                self.map.itemconfigure(
                    self.rect_ids[i][j], outline="black", width=1)

        # Push the new hint tiles into the queue (as numpy array)
        self.hints.put(hint_tiles)
        for (i, j) in hint_tiles:
            cell_type = map.tile_type(i, j)
            self.map.tag_raise(self.rect_ids[i][j])
            self.map.tag_raise(self.text_ids[i][j])
            self.map.itemconfigure(self.rect_ids[i][j], outline="red", width=3)
            self.map.itemconfigure(self.text_ids[i][j],
                                   text=cell_type,
                                   anchor="center",
                                   font=("Roboto bold", self.cell_font_size),
                                   fill=tile_colors.get(cell_type, "black"))

    # Display cells with no treasure, color them as grey
    def display_no_treasure(self, no_treasure_tiles):
        for (i, j) in no_treasure_tiles:
            self.map.tag_raise(self.rect_ids[i][j])
            self.map.itemconfigure(self.rect_ids[i][j], fill="light grey")

    # Display map
    def display(self):
        for i in range(self.cols):
            for j in range(self.rows):
                cell_color = colors.get(map.get_region(i, j), default)
                cell_type = map.tile_type(i, j)

                # Numbers for Ox coordinate
                if j == 0:
                    self.xcoor.create_text((i+0.5)*self.cell_width,
                                           (j+0.5)*self.cell_height,
                                           text=i,
                                           anchor="center",
                                           font=("Roboto bold",
                                                 self.cell_font_size),
                                           fill="gray80")
                # Numbers for Oy coordinate
                if i == 0:
                    self.ycoor.create_text((i+0.5)*self.cell_width,
                                           (j+0.5)*self.cell_height,
                                           text=j,
                                           anchor="center",
                                           font=("Roboto bold",
                                                 self.cell_font_size),
                                           fill="gray80")

                # Create and color the Canvas rectangles, as well as
                # appending them into the ObjectID list
                self.rect_ids[i][j] = self.map.create_rectangle(i*self.cell_width,  # x top left corner
                                                                j*self.cell_height,  # y top left corner
                                                                # x bot right corner
                                                                (i+1) * \
                                                                self.cell_width,
                                                                # y bot right corner
                                                                (j+1) * \
                                                                self.cell_height,
                                                                fill=cell_color)

                # Add label into the rectangles with it's corresponding tile types
                # (Mountain, Prison, Treasure)
                self.text_ids[i][j] = self.map.create_text((i+0.5)*self.cell_width,
                                                           (j+0.5) *
                                                           self.cell_height,
                                                           text=cell_type,
                                                           anchor="center",
                                                           font=(
                                                               "Roboto bold", self.cell_font_size),
                                                           fill=tile_colors.get(cell_type, "black"))


class LogDisplay(tk.CTkFrame):
    '''
        Display log, should receive inputs from agent and game rule
        as CONTENT (string) in the insert_log function
    '''

    def __init__(self, *args, header_name="LOGS", log_height=420, log_width=450, **kwargs):
        super().__init__(*args, **kwargs)

        self.header_name = header_name
        self.header = tk.CTkLabel(
            self, text=self.header_name, font=("Roboto", 24))
        self.header.grid(row=0, column=0, padx=10, pady=10)

        self.log_height = log_height
        self.log_width = log_width

        self.text = tk.CTkTextbox(self, width=self.log_width,
                                  height=self.log_height,
                                  font=("Roboto", 21))
        self.text.grid(row=1, column=0, padx=20, pady=10)

    def insert_log(self, content="> Game start"):
        self.text.configure(state="normal")  # Set log to read and write
        self.text.insert(tk.END, f"{content}\n")
        self.text.configure(state="disabled") # Set log to read-only


class RegionDisplay(tk.CTkFrame):
    '''
        Display the region labels
    '''

    def __init__(self, *args, width=450, height=200, num_regions, **kwargs):
        super().__init__(*args, **kwargs)

        self.header_name = "Region"
        self.header = tk.CTkLabel(
            self, text=self.header_name, font=("Roboto", 24))
        self.header.grid(row=0, column=0, padx=10, pady=10)

        self.width = width
        self.height = height
        self.num_regions = num_regions

        self.upper_region_count = round(num_regions/2)
        self.canvas_width = width//(self.upper_region_count+2)
        self.canvas_height = height//4

        self.no_region = tk.CTkLabel(
            self, text="No treasure", font=("Roboto", 24))
        self.no_region.grid(
            row=0, column=self.upper_region_count, padx=20, pady=20)

    def display(self):
        count = 0
        for i in range(2):
            for j in range(self.upper_region_count):
                region_color = colors.get(count, default)
                region = tk.CTkCanvas(master=self, width=self.canvas_width,
                                      height=self.canvas_height,
                                      bg=region_color)
                region.create_text(self.canvas_width//2, self.canvas_height//2,
                                   text=count,
                                   anchor="center",
                                   font=("Roboto bold", 16))
                region.grid(row=i+1, column=j, padx=10, pady=10)
                count += 1
                if count == self.num_regions:
                    break
        no_treasure_region = tk.CTkCanvas(master=self, width=self.canvas_width,
                                          height=self.canvas_height,
                                          bg="light grey")
        no_treasure_region.grid(
            row=1, column=self.upper_region_count, padx=10, pady=10)


class NoteDisplay(tk.CTkFrame):
    '''
        Display notes, should receive input from game rule
        as CONTENT (string) in insert_note function
    '''

    def __init__(self, *args, header_name="Note", height=100, width=450, **kwargs):
        super().__init__(*args, **kwargs)

        self.header_name = header_name
        self.header = tk.CTkLabel(
            self, text=self.header_name, font=("Roboto", 24))
        self.header.grid(row=0, column=0, padx=10, pady=10)

        self.height = height
        self.width = width

        self.label = tk.CTkLabel(self, width=self.width,
                                 height=self.height,
                                 font=("Roboto", 21),
                                 text="First note",
                                 anchor="nw",
                                 padx=20, pady=10)
        self.label.grid(row=1, column=0, padx=20)

    def insert_note(self, content="First note"):
        self.label.configure(text=f"{content}")


if __name__ == "__main__":
    # map = Map(16, 16)
    # map.generate_map()

    game = Game(16, 16)
    map = game.map_manager
    map.generate_map()
    (width, height) = map.get_map_shape()

    app = App(game=game, map_cols=width, map_rows=height)

    sv_ttk.set_theme("dark")    # Set theme

    app.maxsize(1600, 1000)     # Make the window fixed size
    app.minsize(1600, 1000)
    app.geometry("1600x1000")

    app.draw_map()
    app.draw_side_information()

    app.resizable(False, False)
    app.mainloop()
