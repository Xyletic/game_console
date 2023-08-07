import math
from xyletic_hardware.screen import Screen
from xyletic_hardware.joystick import Joystick
import system_data.system_colors as colors
import snakegame_controller as game
import random
import displayio


class Snake:
    def __init__(self, screen: Screen, controller: game.SnakeGame, group):
        self.x = game.grid_start_x + game.grid_size * 2
        self.y = game.grid_start_y + int(game.grid_height / 2)
        self.direction = 0
        self.tails = []
        self.max_length = 100
        self.group = group
        self.sprite = displayio.TileGrid(controller.snake_head_bitmaps[1], pixel_shader=controller.snake_head_palettes[1], x=self.x, y=self.y)
        self.sprite.flip_x = True
        self.group.append(self.sprite)
        self.screen = screen
        self.controller = controller
        self.last_direction = 0

    def move_snake(self):
        if(len(self.tails) > 0):
            lastTail = self.tails[-1]
            frontTail = self.tails[0]
            self.tails.remove(lastTail)
            if(frontTail != lastTail):
                lastTail.move_position(self.x, self.y, frontTail.dir)
            else:
                lastTail.move_position(self.x, self.y)
            self.tails.insert(0, lastTail)
            self.tails[-1].update_to_end_sprite()
        if(self.direction == 0):
            self.x += game.grid_size
            if(self.direction != self.last_direction):
                self.group.remove(self.sprite)
                self.sprite = displayio.TileGrid(self.controller.snake_head_bitmaps[1], pixel_shader=self.controller.snake_head_palettes[1], x=self.x, y=self.y)
                self.sprite.flip_x = True
                self.group.append(self.sprite)
        if(self.direction == 90):
            self.y += game.grid_size
            if(self.direction != self.last_direction):
                self.group.remove(self.sprite)
                self.sprite = displayio.TileGrid(self.controller.snake_head_bitmaps[0], pixel_shader=self.controller.snake_head_palettes[0], x=self.x, y=self.y)
                self.sprite.flip_y = True
                self.group.append(self.sprite)
        if(self.direction == 180):
            self.x -= game.grid_size
            if(self.direction != self.last_direction):
                self.group.remove(self.sprite)
                self.sprite = displayio.TileGrid(self.controller.snake_head_bitmaps[1], pixel_shader=self.controller.snake_head_palettes[1], x=self.x, y=self.y)
                self.group.append(self.sprite)
        if(self.direction == 270):
            self.y -= game.grid_size
            if(self.direction != self.last_direction):
                self.group.remove(self.sprite)
                self.sprite = displayio.TileGrid(self.controller.snake_head_bitmaps[0], pixel_shader=self.controller.snake_head_palettes[0], x=self.x, y=self.y)
                self.group.append(self.sprite)

        
        if(self.x >= game.grid_start_x + game.grid_width):
            self.x = game.grid_start_x
        if (self.y >= game.grid_start_y + game.grid_height):
            self.y = game.grid_start_y
        if(self.x < game.grid_start_x):
            self.x = (game.grid_start_x + game.grid_width) - game.grid_size
        if(self.y < game.grid_start_y):
            self.y = (game.grid_start_y + game.grid_height) - game.grid_size
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.last_direction = self.direction
        
    def apple_eaten(self):
        if(len(self.tails) < self.max_length):
            if(len(self.tails) > 0):
                self.tails.append(SnakeTail(self.tails[-1].sprite.x, self.tails[-1].sprite.y, self.tails[-1].dir, self.controller, self.group))
            else:
                self.tails.append(SnakeTail(self.x, self.y, self.direction, self.controller, self.group))

    def player_direction(self, dir):
        if(dir == 180 and self.direction is not 0):
            self.direction = 180
        elif(dir == 0 and self.direction is not 180):
            self.direction = 0
        elif(dir == 270 and self.direction is not 90):
            self.direction = 270
        elif(dir == 90 and self.direction is not 270):
            self.direction = 90


    def pick_direction(self):
        safe_directions = []
        if (self.controller.place_free(self, x_diff=game.grid_size)):
            safe_directions.append(0)
        if (self.controller.place_free(self,x_diff=-game.grid_size)):
            safe_directions.append(180)
        if (self.controller.place_free(self, y_diff=game.grid_size)):
            safe_directions.append(90)
        if (self.controller.place_free(self, y_diff=-game.grid_size)):
            safe_directions.append(270)
        if(len(safe_directions) == 0):
            return

        x_dif = self.x - self.controller.apple.x
        y_dif = self.y - self.controller.apple.y

        target_direction = self.direction

        if(x_dif > game.grid_width / 2 or (x_dif >= game.grid_width / -2 and x_dif < 0)):
            target_direction = 0
        elif((x_dif > 0 and x_dif <= game.grid_width / 2) or x_dif < game.grid_width / -2):
            target_direction = 180
        elif(y_dif > game.grid_height / 2 or (y_dif >= game.grid_height / -2 and y_dif < 0)):
            target_direction = 90
        elif((y_dif > 0 and y_dif <= game.grid_height / 2) or y_dif < game.grid_height / -2):
            target_direction = 270

        if self.direction == target_direction and target_direction in safe_directions:
            # Continue in the same direction if it's safe and leads towards the apple
            return
        elif target_direction in safe_directions:
            # Go towards the apple if it's safe, even if it requires a turn
            self.direction = target_direction
        else:
            # If the direction towards the apple is not safe, pick the safest direction
            # that is closest to the target direction
            safe_directions.sort(key=lambda d: min(abs(d - target_direction), abs(d - target_direction + 360), abs(d - target_direction - 360)))
            self.direction = safe_directions[0]



class SnakeTail:
    def __init__(self, x, y, dir, controller: game.SnakeGame, group):
        self.group = group
        self.controller = controller
        self.dir = dir
        if(dir == 180 or dir == 0):
            self.sprite = displayio.TileGrid(self.controller.snake_body_bitmaps[4], pixel_shader=self.controller.snake_body_palettes[4], x=x, y=y)
            if(dir == 0):
                self.sprite.flip_x = True
        else:
            self.sprite = displayio.TileGrid(self.controller.snake_body_bitmaps[3], pixel_shader=self.controller.snake_body_palettes[3], x=x, y=y)
            if(dir == 90):
                self.sprite.flip_y = True
        self.group.append(self.sprite)
        #self.tail_segment = screen.draw_circle(self.x, self.y, math.floor(game.grid_size /2), fill=fill_color, outline=outline_color)

    def move_position(self, x, y, behind_dir=None):
        self.dir = self.controller.player_one.direction
        if(behind_dir == None):
            self.sprite.x = x
            self.sprite.y = y
            return
        self.group.remove(self.sprite)
        if(behind_dir == self.controller.player_one.direction):
            # Straight
            if(self.dir == 180 or self.dir == 0):
                self.sprite = displayio.TileGrid(self.controller.snake_body_bitmaps[1], pixel_shader=self.controller.snake_body_palettes[1], x=x, y=y)
            else:
                self.sprite = displayio.TileGrid(self.controller.snake_body_bitmaps[0], pixel_shader=self.controller.snake_body_palettes[0], x=x, y=y)
        else:
            # Corner
            self.sprite = displayio.TileGrid(self.controller.snake_body_bitmaps[2], pixel_shader=self.controller.snake_body_palettes[2], x=x, y=y)
            if(self.dir == 0 and behind_dir == 90):
                self.sprite.flip_y = True
            elif(self.dir == 90 and behind_dir == 0):
                self.sprite.flip_x = True
            elif(self.dir == 180):
                self.sprite.flip_x = True
                if(behind_dir == 90):
                    self.sprite.flip_y = True
            elif(self.dir == 270):
                self.sprite.flip_y = True
                if(behind_dir == 0):
                    self.sprite.flip_x = True
        self.group.append(self.sprite)
    
    def update_to_end_sprite(self):
        self.group.remove(self.sprite)
        if(self.dir == 180 or self.dir == 0):
            self.sprite = displayio.TileGrid(self.controller.snake_body_bitmaps[4], pixel_shader=self.controller.snake_body_palettes[4], x=self.sprite.x, y=self.sprite.y)
            if(self.dir == 0):
                self.sprite.flip_x = True
        else:
            self.sprite = displayio.TileGrid(self.controller.snake_body_bitmaps[3], pixel_shader=self.controller.snake_body_palettes[3], x=self.sprite.x, y=self.sprite.y)
            if(self.dir == 90):
                self.sprite.flip_y = True
        self.group.append(self.sprite)