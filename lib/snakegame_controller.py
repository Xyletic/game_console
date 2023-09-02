from hardware_controller import Hardware
from snakegame_data.snakegame_snake import Snake
from snakegame_data.snakegame_apple import Apple
import system_data.system_colors as colors
import adafruit_imageload
import displayio
import time
import asyncio
import math
import random
import screenshot_controller
from xyletic_game_engine.navigation import Navigation
from xyletic_game_engine.vector_two import Vector2
from xyletic_game_engine.collision_rectangle import CollisionRectangle

grid_size = 6
grid_start_x = 0
grid_start_y = 18
grid_width = math.floor(160 / grid_size) * grid_size
grid_height = math.floor(110 / grid_size) * grid_size
grid_cell_width = int(grid_width / grid_size)
grid_cell_height = int(grid_height / grid_size)
snake_size = 6


class SnakeGame:
    # We want to move this code to a start game function instead
    def __init__(self, hardware: Hardware) -> None:
        self.hardware = hardware
        self.hardware.joystick.debounce_time = .5
        self.playing = False
        self.player_one_score = 0
        self.highscore = 0
        self.path = None
        self.hardware.display.reset()
        self.image_load()
        self.setup_screen()
        self.player_one = Snake(self.hardware.display, self, self.group)
        self.apple = Apple(self, self.group)
        self.restart()


    def load_images(self, paths, make_transparent=False):
        bitmaps = []
        palettes = []
        for path in paths:
            bitmap, palette = adafruit_imageload.load(path, bitmap=displayio.Bitmap, palette=displayio.Palette)
            if(make_transparent):
                palette.make_transparent(0)
            bitmaps.append(bitmap)
            palettes.append(palette)
        return bitmaps, palettes


    def image_load(self):
        snake_head_paths = ["/assets/snake/snake_head_up.bmp", "/assets/snake/snake_head_left.bmp"]
        self.snake_head_bitmaps, self.snake_head_palettes = self.load_images(snake_head_paths)

        snake_body_paths = ["/assets/snake/snake_body_straight_up.bmp", "/assets/snake/snake_body_straight_left.bmp", "/assets/snake/snake_body_corner.bmp", "/assets/snake/snake_body_tail_up.bmp", "/assets/snake/snake_body_tail_left.bmp"]
        self.snake_body_bitmaps, self.snake_body_palettes = self.load_images(snake_body_paths)

        self.apple_bitmap, self.apple_palette = adafruit_imageload.load("/assets/snake/apple.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)

        foliage_paths = [f"/assets/snake/foliage_{i}.bmp" for i in range(1, 7)]
        self.foliage_bitmaps, self.foliage_palettes = self.load_images(foliage_paths, make_transparent=True)
    
    def setup_screen(self):
        self.group = self.hardware.display.create_group()
        # Graphic Setup
        self.hardware.display.draw_rect(0, 0, 160, 128, fill=0x1c2638, group=self.group) # Background
        self.hardware.display.draw_line(grid_start_x, grid_start_y - 1, grid_width, grid_start_y - 1, 0xdaf2e9, group=self.group) # Divider Line
        self.hardware.display.draw_text(5, 10, "P1:", 1, 0x95e0cc, group=self.group) # Player 1 Score Label
        self.p1_score_display = self.hardware.display.draw_text(25, 10, str(self.player_one_score), 1, 0xdaf2e9, group=self.group) # Player 1 Score Value
        self.hardware.display.draw_text(50, 10, "HS:", 1, 0x95e0cc, group=self.group) # Highscore Label
        self.highscore_display = self.hardware.display.draw_text(70, 10, str(self.highscore), 1, 0xdaf2e9, group=self.group) # Highscore Value 
        for _ in range(20):
            #add foliage
            c = random.randint(0, len(self.foliage_bitmaps) - 1)
            self.group.append(displayio.TileGrid(self.foliage_bitmaps[c], pixel_shader=self.foliage_palettes[c], x=random.randint(grid_start_x, grid_start_x + grid_width - 6), y=random.randint(grid_start_y, grid_start_y + grid_height - 6)))
            
        # if(not self.playing):
        #     self.hardware.display.draw_text(5, 115, "Press", 1, colors.WHITE, group=self.group) # Score Label
        #     self.hardware.display.draw_text(41, 115, "blue", 1, colors.LIGHT_BLUE, group=self.group) # Score Label
        #     self.hardware.display.draw_text(70, 115, "to play!", 1, colors.WHITE, group=self.group) # Score Label


    async def process(self):
        if(self.hardware.menu_button.was_pressed()):
            return 0
        await asyncio.sleep(self.max_wait / 1000)
        if(self.playing):
            # Player is playing
            self.player_one.player_direction(self.hardware.joystick.get_last_direction())
        else:
            self.player_one.pick_direction() # AI is playing
            if(self.hardware.blue_button.is_pressed()):
                self.playing = True
                self.restart()
        
        # Move the snakes
        self.player_one.move_snake()

        # Check for collisions
        if(not self.place_free(self.player_one)):
            await self.game_over()
        
        # P1 eats apple
        if(self.apple.x == self.player_one.x and self.apple.y == self.player_one.y):
            self.player_one_score += 1
            self.p1_score_display.text = str(self.player_one_score)
            self.eat_apple(self.player_one)
        return -1

    def eat_apple(self, player: Snake):
        asyncio.create_task(self.hardware.speaker.play_song_async(["C5","G5"], [.1,.1]))
        player.apple_eaten()
        if(self.player_one_score % 5 == 0 and self.max_wait > 100):
            self.max_wait -= 20
        self.apple.move_position()

    def restart(self):
        if(self.player_one_score > self.highscore):
            self.highscore = self.player_one_score
        self.player_one_score = 0
        self.p1_score_display.text = str(self.player_one_score)
        self.highscore_display.text = str(self.highscore)
        self.max_wait = 300
        self.player_one.reset()
        self.apple.move_position()
        if(self.playing):
           self.hardware.blue_button.LED_off()
           self.hardware.joystick.debounce_time = .01
        else:
           self.hardware.blue_button.pulse()
           self.hardware.joystick.debounce_time = .5
        


    def place_free(self, obj, x_diff=0, y_diff=0):
        if(obj.x + x_diff < grid_start_x or obj.x + x_diff >= grid_start_x + grid_width or obj.y + y_diff < grid_start_y or obj.y + y_diff >= grid_start_y + grid_height):
            return False
        if(obj is not self.player_one):
            if(self.player_one.x == obj.x + x_diff and self.player_one.y == obj.y + y_diff):
                return False
        for tail in self.player_one.tails:
            if(obj.x + x_diff == tail.sprite.x and obj.y + y_diff == tail.sprite.y):
                return False
        return True


    async def game_over(self):
        gameover_group = self.hardware.display.create_group()
        self.hardware.display.draw_text(25, 65, "Game Over!", 2, 0xFFFF00, group=gameover_group)
        asyncio.create_task(self.hardware.speaker.play_note_async("E2", 1))
        self.playing = False
        await asyncio.sleep(2.5)
        #remove game over text
        self.hardware.display.remove_element(gameover_group)
        self.restart()


    def quit(self):
        pass