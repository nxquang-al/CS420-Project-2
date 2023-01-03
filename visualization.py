import tkinter
import customtkinter as tk
from tkinter import ttk
import sv_ttk
import numpy as np
import random
import math
import argparse

from map import Map
from queue import Queue
from game import Game
from utils import read_input_file, write_logs_file

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
light_sienna = "sienna1"
dark_sienna = "sienna3"
light_gray = "snow3"
dark_gray = "snow4"
light_gold = "light goldenrod"
default = "CadetBlue4"

colors = {
    0: sea_color,
    1: soil_color,
    2: light_pink,
    3: light_green,
    4: dark_green,
    5: sand_color,
    6: dark_pink,
    7: light_sienna,
    8: dark_sienna,
    9: light_gray,
    10: dark_gray,
    11: light_gold,
    12: default,
}

tile_colors = {
    'P': "gray90",
    'T': "gold"
}

# Set color theme (for button and stuff)
tk.set_default_color_theme("dark-blue")


class App(tk.CTk):
    '''
        Application, responsible for managing main grids, components
        and button onClick
    '''

    def __init__(self, game: Game, map_cols=16, map_rows=16):
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
        self.side_information = SideInformation(
            self.game.map_manager.num_regions, self)
        self.side_information.grid(row=0, column=1, padx=20, pady=20)

        # Button to show Next turn
        self.button = tk.CTkButton(self, text="Next turn", font=(
            "Roboto", 20), command=self.next_turn)
        self.button.grid(row=1, column=1, padx=10, pady=0)

        self.count = 0      # For testing

    def draw_map(self):
        self.map_display.display()  # Display map

        # Display agent
        agent_pos = self.game.get_agent_pos()
        self.map_display.move_agent(agent_pos[0], agent_pos[1])

    def draw_side_information(self):
        self.game.log_init()
        log_content = self.game.log()

        self.side_information.draw_log(log_content)  # Display Logs
        self.side_information.draw_region()  # Display Region labels

    # Button to move onto the next state
    def next_turn(self, log_content="", note_content=""):

        if self.game.is_win or self.game.is_lose:
            self.button.configure(state="disabled")
            pass

        self.game.next_turn()

        self.count += 1     # For testing

        log_content = self.game.log()

        self.side_information.log_display.insert_log(log_content)
        self.side_information.note_display.insert_note(
            f"Note content {self.count}")

        agent_pos = self.game.get_agent_pos()
        print(f"Agent pos: {agent_pos}")

        pirate_pos, pirate_is_free = self.game.get_pirate_pos()
        if pirate_is_free:
            self.map_display.move_pirate(pirate_pos[0], pirate_pos[1])
            print(f"Pirate pos: {pirate_pos}")

        # self.map_display.move_agent()
        self.map_display.move_agent(agent_pos[0], agent_pos[1])

        hint_tiles = self.game.pass_hint_tiles()
        self.map_display.show_hints(hint_tiles)

        scan_area = self.game.pass_scan_area()

        self.map_display.display_no_treasure(scan_area)

        agent_kb = self.game.get_kb()
        no_treasure = []
        for i in range(agent_kb.shape[0]):
            for j in range(agent_kb.shape[1]):
                if agent_kb[i][j] == False and map.is_sea((i, j)) == False:
                    no_treasure.append([i, j])

        self.map_display.display_no_treasure(no_treasure)


class SideInformation(tk.CTkFrame):
    '''
        Responsible for the half right of the window, manage Logs, Regions and Note
    '''

    def __init__(self, num_regions, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.region_display = RegionDisplay(self, num_regions=num_regions)
        self.region_display.grid(row=0, column=0, padx=10, pady=10)

        self.log_display = LogDisplay(self)
        self.log_display.grid(row=1, column=0, padx=10, pady=10)

        self.note_display = NoteDisplay(self)
        self.note_display.grid(row=2, column=0, padx=10, pady=10)

    def draw_log(self, content=None):
        self.log_display.insert_log(content)

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

        # Queue for agent position, each state the old_position will be pop out.
        # The queue maintains its only element
        self.agent_pos = Queue()
        self.agent_text_id = None
        self.agent_rec_id = None

        self.rect_ids = np.empty(
            (rows, cols), dtype=int)   # ObjectID for easier
        # modification of tkinter canvas
        self.text_ids = np.empty((rows, cols), dtype=int)

        self.pirate_pos = Queue()
        self.pirate_text_id = None
        self.pirate_rec_id = None

        self.hints = Queue()

    # Randomize the position of agent FOR TESTING

    def move_agent(self, x_des=5, y_des=5):
        self.agent_rec_id = self.map.create_rectangle((x_des)*self.cell_width,
                                                      (y_des+0.5) *
                                                      self.cell_height,
                                                      (x_des+0.5) *
                                                      self.cell_width,
                                                      (y_des+1) *
                                                      self.cell_height,
                                                      fill="yellow")

        self.agent_text_id = self.map.create_text((x_des+0.25)*self.cell_width,
                                                  (y_des+0.75) *
                                                  self.cell_height,
                                                  text='A',
                                                  anchor="center",
                                                  font=("Roboto bold",
                                                        self.cell_font_size - 3),
                                                  fill="orange red")

        self.agent_pos.put(self.agent_text_id)
        self.agent_pos.put(self.agent_rec_id)

        if self.agent_pos.qsize() > 2:
            self.map.delete(self.agent_pos.get())
            self.map.delete(self.agent_pos.get())

    def move_pirate(self, x_des=5, y_des=5):
        self.pirate_rec_id = self.map.create_rectangle((x_des+0.5)*self.cell_width,
                                                       y_des * self.cell_height,
                                                       (x_des+1) *
                                                       self.cell_width,
                                                       (y_des+0.5) *
                                                       self.cell_height,
                                                       fill="PaleVioletRed4")

        self.pirate_text_id = self.map.create_text((x_des+0.75)*self.cell_width,
                                                   (y_des+0.25) *
                                                   self.cell_height,
                                                   text='Pi',
                                                   anchor="center",
                                                   font=("Roboto bold",
                                                         self.cell_font_size - 3),
                                                   fill="black")

        self.pirate_pos.put(self.pirate_text_id)
        self.pirate_pos.put(self.pirate_rec_id)

        if self.pirate_pos.qsize() > 2:
            self.map.delete(self.pirate_pos.get())
            self.map.delete(self.pirate_pos.get())

    # Display the hint tiles as cell with red borders.
    def show_hints(self, hint_tiles):
        if hint_tiles is None or not len(hint_tiles):
            return

        # Pop out and remove the old hints (both in queue and on map display)
        if not self.hints.empty():
            old_hints = self.hints.get()
            for tile in old_hints:
                for (i, j) in tile:
                    self.map.tag_lower(self.rect_ids[i][j])
                    self.map.itemconfigure(
                        self.rect_ids[i][j], outline="black", width=1)

        # Push the new hint tiles into the queue (as numpy array)
        self.hints.put(hint_tiles)
        for tile in hint_tiles:
            for (i, j) in tile:
                cell_type = map.tile_type(i, j)
                self.map.tag_raise(self.rect_ids[i][j])
                self.map.tag_raise(self.text_ids[i][j])
                self.map.itemconfigure(
                    self.rect_ids[i][j], outline="red", width=(3 if self.cols < 48 else 2))
                self.map.itemconfigure(self.text_ids[i][j],
                                       text=cell_type,
                                       anchor="center",
                                       font=("Roboto bold",
                                             self.cell_font_size),
                                       fill=tile_colors.get(cell_type, "black"))

        self.map.tag_raise(self.agent_rec_id)
        self.map.tag_raise(self.agent_text_id)
        self.map.tag_raise("Treasure")

        if self.pirate_rec_id != None:
            self.map.tag_raise(self.pirate_rec_id)
            self.map.tag_raise(self.pirate_text_id)

    # Display cells with no treasure, color them as grey
    def display_no_treasure(self, no_treasure_tiles):
        for (i, j) in no_treasure_tiles:
            self.map.tag_raise(self.rect_ids[i][j])
            self.map.itemconfigure(self.rect_ids[i][j], fill="thistle4")
        self.map.tag_raise('M')
        self.map.tag_raise('P')
        self.map.tag_raise("Treasure")
        self.map.tag_raise('T')
        self.map.tag_raise(self.agent_rec_id)
        self.map.tag_raise(self.agent_text_id)
        if self.pirate_rec_id != None:
            self.map.tag_raise(self.pirate_rec_id)
            self.map.tag_raise(self.pirate_text_id)

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
                if cell_type == 'T':
                    self.map.create_rectangle((i+0.15)*self.cell_width,
                                              (j+0.15) *
                                              self.cell_height,
                                              (i+0.85) *
                                              self.cell_width,
                                              (j+0.85) *
                                              self.cell_height,
                                              tags="Treasure",
                                              fill="gray10")

                # Add label into the rectangles with it's corresponding tile types
                # (Mountain, Prison, Treasure)
                self.text_ids[i][j] = self.map.create_text((i+0.5)*self.cell_width,
                                                           (j+0.5) *
                                                           self.cell_height,
                                                           text=cell_type,
                                                           anchor="center",
                                                           tags=cell_type,
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
                                  font=("Roboto", 19))
        self.text.grid(row=1, column=0, padx=20, pady=10)

    def insert_log(self, content="> Game start"):
        if content == "":
            pass
        self.text.configure(state="normal")  # Set log to read and write
        self.text.insert(tk.END, f"{content}\n")
        self.text.configure(state="disabled")  # Set log to read-only


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
        self.num_regions = num_regions + 1

        self.upper_region_count = math.ceil(self.num_regions/2)
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
                                          bg="thistle4")
        hint_tiles = tk.CTkCanvas(master=self, width=self.canvas_width,
                                  height=self.canvas_height,
                                  bg="gray16",
                                  highlightbackground="red")
        hint_tiles.create_text(self.canvas_width//2, self.canvas_height//2,
                               text="Hint",
                               anchor="center",
                               font=("Roboto bold", 16),
                               fill="gray90")

        no_treasure_region.grid(
            row=1, column=self.upper_region_count, padx=10, pady=10)
        hint_tiles.grid(
            row=2, column=self.upper_region_count, padx=10, pady=10)


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

    parser = argparse.ArgumentParser(description="CS420 - Project 2")
    parser.add_argument('-r', '--read', type=str, nargs=1, metavar='file_name',
                        default=None, help="Path to the input file")
    parser.add_argument('-g', '--generate', type=int, nargs=2, metavar=(
        'width', 'height'), help="Expected width and height of the map")
    args = parser.parse_args()

    game = None
    input_mode = 0
    file_path = ''
    if args.read is not None:
        file_path = args.read[0]
        input_data = read_input_file(file_path)
        game = Game(input_data)
    elif args.generate is not None:
        input_mode = 1
        width = args.generate[0]
        height = args.generate[1]
        game = Game(input_data=[width, height])

    # game = Game(32, 32)
    map = game.map_manager
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

    if input_mode == 0:
        id_testcase = file_path[-6:-4]
        file_name = 'LOG_' + id_testcase + '.txt'
        write_logs_file(file_name=file_name, logs=game.full_logs)
