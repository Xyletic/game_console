import adafruit_imageload
import displayio
import asyncio
import spaceshooter_controller as game
import random
import gc

class BasicEnemy:
    def __init__(self, group : displayio.Group, bitmap, primary_palette, hit_palette) -> None:
        #gc.collect()
        #start_mem = gc.mem_free()
        #print("Memory free:", start_mem)
        self.bitmap = bitmap
        self.palette = primary_palette
        self.hit_palette = hit_palette
        self.health = 3
        self.group = group
        self.x = game.game_start_x + game.game_width + 5
        y = random.randrange(game.game_start_y + 5, game.game_start_y + game.game_height - 21)
        self.sprite = displayio.TileGrid(bitmap, pixel_shader=self.palette, x=self.x, y=y)
        group.append(self.sprite)
        self.ydir = 90
        self.xspeed = .2
        #print("BasicEnemy memory used:", start_mem - gc.mem_free())
    
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
    
    async def hit(self, damage):
        self.health -= damage
        if(self.health > 0):
            self.group.remove(self.sprite)
            self.sprite = displayio.TileGrid(self.bitmap, pixel_shader=self.hit_palette,x=self.sprite.x, y=self.sprite.y)
            self.group.append(self.sprite)
            await asyncio.sleep(.04)
            self.group.remove(self.sprite)
            self.sprite = displayio.TileGrid(self.bitmap, pixel_shader=self.palette,x=self.sprite.x, y=self.sprite.y)
            self.group.append(self.sprite)
    
    def remove(self):
        self.group.remove(self.sprite)