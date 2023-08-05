import displayio
import spaceshooter_controller as game
from xyletic_hardware.screen import Screen
import system_data.system_colors as colors

class PlayerLaser:
    def __init__(self, x, y, screen : Screen, group : displayio.Group) -> None:
        self.group = group
        self.screen = screen
        self.sprite = screen.draw_line(x, y, x+5, y, colors.RED, group)
    
    def is_colliding(self, x1, y1, x2, y2) -> bool:
        startx = self.sprite.x - game.laser_speed
        endx = self.sprite.x + 5
        if(y1 <= self.sprite.y and y2 >= self.sprite.y):
            if(startx <= x2 and endx >= x1):
                return True
        return False

    def move(self):
        self.sprite.x += game.laser_speed

    def remove(self):
        self.screen.remove_element(self.sprite, self.group)