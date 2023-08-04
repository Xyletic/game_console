from xyletic_hardware.screen import Screen
import spaceshooter_controller as game
from system_data import system_colors as colors
import random

class Star:
    def __init__(self, screen: Screen, group) -> None:
        x = random.randint(game.game_start_x, game.game_start_x + game.game_width)
        y = random.randint(game.game_start_y + 3, game.game_start_y + game.game_height - 3)
        self.visual = screen.draw_circle(x,y,1,fill=colors.WHITE, group=group)
        self.xspeed = random.choice([1,2,3,4,5,6])

    
    def reset(self):
        self.visual.x = game.game_start_x + game.game_width
        self.visual.y = random.randint(game.game_start_y + 3, game.game_start_y + game.game_height - 3)
        self.xspeed = random.choice([1,2,3,4,5,6])

    def move(self):
        self.visual.x -= self.xspeed
        if(self.visual.x < game.game_start_x - 5):
            self.reset()