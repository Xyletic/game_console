import adafruit_imageload
import displayio
import asyncio
import spaceshooter_controller as game
import random

class BasicEnemy:
    def __init__(self, group : displayio.Group) -> None:
        self.health = 2
        self.group = group
        self.x = game.game_start_x + game.game_width + 5
        # Load the image
        self.bitmap, self.primary_palette = adafruit_imageload.load("/assets/spaceshooter/enemy_ship.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        self.white_palette = displayio.Palette(len(self.primary_palette))
        for i, color in enumerate(self.primary_palette):
            if(color != 0):
                self.white_palette[i] = 0xFFFFFF
        # Modify palette to make black pixels transparent
        self.primary_palette.make_transparent(0)
        self.white_palette.make_transparent(0)
        # Create a tilegrid using the bitmap and palette
        y = random.randrange(game.game_start_y + 5, game.game_start_y + game.game_height - 21)
        self.sprite = displayio.TileGrid(self.bitmap, pixel_shader=self.primary_palette, x=self.x, y=y)
        group.append(self.sprite)
        self.ydir = 90
        self.xspeed = .2
    
    def move(self):
        self.x -= self.xspeed
        roundedx = round(self.x)
        if(roundedx != self.sprite.x):
            self.sprite.x = roundedx

        
    def bounce(self):
        self.move(-1, self.ydir)

    def get_width(self):
        return self.sprite.tile_width * self.sprite.width
    
    def get_height(self):
        return self.sprite.tile_height * self.sprite.height
    
    async def hit(self):
        self.health -= game.laser_damage
        if(self.health > 0):
            self.group.remove(self.sprite)
            self.sprite = displayio.TileGrid(self.bitmap, pixel_shader=self.white_palette,x=self.sprite.x, y=self.sprite.y)
            self.group.append(self.sprite)
            await asyncio.sleep(.04)
            self.group.remove(self.sprite)
            self.sprite = displayio.TileGrid(self.bitmap, pixel_shader=self.primary_palette,x=self.sprite.x, y=self.sprite.y)
            self.group.append(self.sprite)
        else:
            pass
            #self.remove()
    
    def remove(self):
        self.group.remove(self.sprite)