import adafruit_imageload
import displayio
import spaceshooter_controller as game

class PlayerShip:
    def __init__(self, group : displayio.Group) -> None:
        self.health = 3
        # Load the image
        bitmap, palette = adafruit_imageload.load("/assets/spaceshooter/player_ship.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        # Modify palette to make black pixels transparent
        palette.make_transparent(0)
        # Create a tilegrid using the bitmap and palette
        self.sprite = displayio.TileGrid(bitmap, pixel_shader=palette, y= game.game_start_y + (int)(game.game_height / 2))
        self.sprite.flip_x = True
        group.append(self.sprite)
        self.ydir = 270
    
    def move(self, x, y):
        tempx = None
        tempy = None
        if(x == 0): # Right
            tempx = self.sprite.x + game.player_speed
        elif(x == 180): # Left
            tempx = self.sprite.x - game.player_speed
        if(y == 90): # Down
            tempy = self.sprite.y + game.player_speed
        elif(y == 270): # Up
            tempy = self.sprite.y - game.player_speed
        
        if(tempx != None):
            tempx = max(min(tempx, game.game_start_x + game.game_width - (self.sprite.tile_width * self.sprite.width)), game.game_start_x)
            if(tempx != self.sprite.x):
                self.sprite.x = tempx
        if(tempy != None):
            tempy = max(min(tempy, game.game_start_y + game.game_height - (self.sprite.tile_height * self.sprite.height)), game.game_start_y)
            if(tempy != self.sprite.y):
                self.sprite.y = tempy
            else:
                if(self.ydir == 90):
                    self.ydir = 270
                else:
                    self.ydir = 90
        
    def get_center(self) -> int:
        return self.sprite.y + round(self.sprite.tile_height * self.sprite.height / 2)
    
    def get_front(self) -> int:
        return self.sprite.x + (self.sprite.tile_width * self.sprite.width)
    
    def bounce(self):
        self.move(-1, self.ydir)