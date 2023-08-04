import math
from xyletic_hardware.screen import Screen
from xyletic_hardware.joystick import Joystick
import system_data.system_colors as colors
import snakegame_controller as game
import random


class Snake:
    def __init__(self, screen: Screen, joystick: Joystick, controller: game.SnakeGame, player_num, group):
        if(player_num == 1):
            self.x = game.grid_start_x + game.grid_size * 2
            self.y = game.grid_start_y + int(game.grid_height / 2)
        else:
            self.x = game.grid_start_x + (game.grid_cell_width - 2) * game.grid_size
            self.y = game.grid_start_y + int(game.grid_height / 2)
        self.direction = 0
        self.tails = []
        self.max_length = 100
        if(player_num == 1):
            self.primary_color = colors.GREEN
            self.secondary_color = colors.DARK_GREEN
        else:
            self.primary_color = colors.RED
            self.secondary_color = colors.DARK_RED
        self.snake_head = screen.draw_circle(self.x, self.y, math.floor(game.grid_size / 2), fill=self.primary_color, outline=colors.WHITE, group=group)
        #self.snake_head = screen.draw_rect(self.x, self.y, game.snake_size, game.snake_size, fill=colors.GREEN)
        self.screen = screen
        self.controller = controller

    def move_snake(self):
        if(len(self.tails) > 0):
            lastTail = self.tails[-1]
            self.tails.remove(lastTail)
            lastTail.move_position(self.x, self.y)
            self.tails.insert(0, lastTail)
        if(self.direction == 0):
            self.x += game.grid_size
        if(self.direction == 90):
            self.y += game.grid_size
        if(self.direction == 180):
            self.x -= game.grid_size
        if(self.direction == 270):
            self.y -= game.grid_size
        if(self.x >= game.grid_start_x + game.grid_width):
            self.x = game.grid_start_x
        if (self.y >= game.grid_start_y + game.grid_height):
            self.y = game.grid_start_y
        if(self.x < game.grid_start_x):
            self.x = (game.grid_start_x + game.grid_width) - game.grid_size
        if(self.y < game.grid_start_y):
            self.y = (game.grid_start_y + game.grid_height) - game.grid_size
        self.snake_head.x = self.x
        self.snake_head.y = self.y
        
    def apple_eaten(self):
        if(len(self.tails) < self.max_length):
            if(len(self.tails) > 0):
                self.tails.append(SnakeTail(self.tails[-1].x + math.floor(game.grid_size /2), self.tails[-1].y + math.floor(game.grid_size /2), self.screen, self.secondary_color, self.primary_color))
            else:
                self.tails.append(SnakeTail(self.x + math.floor(game.grid_size /2), self.y + math.floor(game.grid_size /2), self.screen, self.secondary_color, self.primary_color))

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
    def __init__(self, x, y, screen: Screen, fill_color, outline_color):
        self.x = x
        self.y = y
        self.tail_segment = screen.draw_circle(self.x, self.y, math.floor(game.grid_size /2), fill=fill_color, outline=outline_color)

    def move_position(self, x, y):
        self.x = x
        self.y = y
        self.tail_segment.x = x
        self.tail_segment.y = y