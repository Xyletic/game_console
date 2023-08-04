import snakegame_controller as game
import system_data.system_colors as colors
import math
import random

class Apple:
    def __init__(self, screen, controller, group):
        self.controller = controller
        self.x = 0
        self.y = 0
        self.apple_base = screen.draw_circle(self.x, self.y, math.floor(game.grid_size /2), fill = 0xFF2222, group=group)
        self.apple_leaf = screen.draw_line(self.x, self.y, self.x + 1, self.y, colors.GREEN, group=group)
        self.move_position()


    def move_position(self):
        self.x = game.grid_start_x + (random.randint(0, game.grid_cell_width - 1) * game.grid_size)
        self.y = game.grid_start_y + (random.randint(0, game.grid_cell_height - 1) * game.grid_size)
        while(not self.controller.place_free(self)):
            self.x = game.grid_start_x + (random.randint(0, game.grid_cell_width - 1) * game.grid_size)
            self.y = game.grid_start_y + (random.randint(0, game.grid_cell_height - 1) * game.grid_size)
        self.apple_base.x = self.x
        self.apple_base.y = self.y
        self.apple_leaf.x = self.x
        self.apple_leaf.y = self.y
        