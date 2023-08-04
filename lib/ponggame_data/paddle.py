
from xyletic_hardware.screen import Screen
import system_data.system_colors as colors
import ponggame_controller as game


class Paddle:
    def __init__(self, screen: Screen, player_num: int) -> None:
        self.display = screen
        if(player_num == 1):
            self.x = 7
            self.y = 45
        else:
            self.x = 150
            self.y = 45
        self.paddle_display = self.display.draw_rect(self.x, self.y, game.paddle_width, game.paddle_height, fill=colors.WHITE)
    

    def move(self, direction):
        starty = self.y
        if(direction == 90): # down
            self.y += game.paddle_speed
        elif(direction == 270): # up
            self.y -= game.paddle_speed
        elif(direction == 0): #do nothing
            pass
        if (self.y < game.game_start_y):
            self.y = game.game_start_y
        if (self.y > game.game_start_y + game.game_height - game.paddle_height):
            self.y = game.game_start_y + game.game_height - game.paddle_height
        if(starty != self.y):
            # if we actually moved, update the visual
            self.paddle_display.y = self.y


    def reset(self):
        self.y = 45
        self.paddle_display.y = self.y