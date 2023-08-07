import snakegame_controller as game
import random
import displayio

class Apple:
    def __init__(self, controller, group):
        self.controller = controller
        self.x = 0
        self.y = 0
        self.sprite = displayio.TileGrid(controller.apple_bitmap, pixel_shader=controller.apple_palette, x=self.x, y=self.y)
        group.append(self.sprite)
        self.move_position()


    def move_position(self):
        self.x = game.grid_start_x + (random.randint(0, game.grid_cell_width - 1) * game.grid_size)
        self.y = game.grid_start_y + (random.randint(0, game.grid_cell_height - 1) * game.grid_size)
        while(not self.controller.place_free(self)):
            self.x = game.grid_start_x + (random.randint(0, game.grid_cell_width - 1) * game.grid_size)
            self.y = game.grid_start_y + (random.randint(0, game.grid_cell_height - 1) * game.grid_size)
        self.sprite.x = self.x
        self.sprite.y = self.y
        