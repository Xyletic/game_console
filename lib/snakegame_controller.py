from hardware_controller import Hardware
from snakegame_data.snakegame_snake import Snake
from snakegame_data.snakegame_apple import Apple
import system_data.system_colors as colors
import time
import asyncio
import gc

grid_size = 5
grid_start_x = 0
grid_start_y = 18
grid_width = 160
grid_height = 110
grid_cell_width = int(grid_width / grid_size)
grid_cell_height = int(grid_height / grid_size)
snake_size = 5


class SnakeGame:
    # We want to move this code to a start game function instead
    def __init__(self, hardware: Hardware) -> None:
        self.hardware = hardware
        self.hardware.joystick.debounce_time = .5
        self.playing = False
        self.player_one_score = 0
        self.player_two_score = 0
        self.player_one_has_player = True
        self.player_two_has_player = False
        self.player_one = None
        self.player_count = 1
        if(self.player_count > 1):
            self.player_two = None
        self.apple = None
        self.highscore = 0
        self.chime_state = "high"
        self.group = None
        self.restart()
        
    
    def setup_screen(self):
        self.group = self.hardware.display.create_group()
        # Graphic Setup
        self.hardware.display.draw_rect(0, 0, 160, 128, fill=colors.BLACK, group=self.group) # Background
        self.hardware.display.draw_rect(grid_start_x, grid_start_y, grid_width, grid_height, fill=0x3b2f2f, group=self.group) # Game Area
        self.hardware.display.draw_line(grid_start_x, grid_start_y - 1, grid_width, grid_start_y - 1, colors.WHITE, group=self.group) # Divider Line
        self.hardware.display.draw_text(5, 10, "P1:", 1, colors.GREEN, group=self.group) # Player 1 Score Label
        self.p1_score_display = self.hardware.display.draw_text(25, 10, str(self.player_one_score), 1, colors.WHITE, group=self.group) # Player 1 Score Value
        if(self.player_count > 1):
            self.hardware.display.draw_text(50, 10, "P2:", 1, colors.RED, group=self.group) # Player 2 Score Label
            self.p2_score_display = self.hardware.display.draw_text(70, 10, str(self.player_two_score), 1, colors.WHITE, group=self.group) # Player 2 Score Value
        else:
            self.hardware.display.draw_text(50, 10, "HS:", 1, colors.WHITE, group=self.group) # Highscore Label
            self.hardware.display.draw_text(70, 10, str(self.highscore), 1, colors.WHITE, group=self.group) # Highscore Value
        if(not self.playing):
            self.hardware.display.draw_text(5, 115, "Press", 1, colors.WHITE, group=self.group) # Score Label
            self.hardware.display.draw_text(41, 115, "blue", 1, colors.LIGHT_BLUE, group=self.group) # Score Label
            self.hardware.display.draw_text(70, 115, "to play!", 1, colors.WHITE, group=self.group) # Score Label


    async def process(self):
        if(self.hardware.menu_button.was_pressed()):
            return 0
        await asyncio.sleep(self.max_wait / 1000)
        # if(self.chime_state == "high"):
        #     asyncio.create_task(self.hardware.speaker.play_note("B4"))
        #     self.chime_state = "highoff"
        # elif(self.chime_state == "low"):
        #     asyncio.create_task(self.hardware.speaker.play_note("G4"))
        #     self.chime_state = "lowoff"
        # elif(self.chime_state == "highoff"):
        #     self.chime_state = "low"
        # elif(self.chime_state == "lowoff"):
        #     self.chime_state = "high"
        if(self.playing):
            # Player is playing
            self.player_one.player_direction(self.hardware.joystick.get_last_direction())
        else:
            self.player_one.pick_direction() # AI is playing
            if(self.hardware.blue_button.is_pressed()):
                self.playing = True
                self.restart()
        if(self.player_count > 1 and not self.player_two_has_player):
            self.player_two.pick_direction()
        
        # Move the snakes
        self.player_one.move_snake()
        if(self.player_count > 1):
            self.player_two.move_snake()

        # Check for collisions
        if(not self.place_free(self.player_one)):
            await self.game_over()
        if(self.player_count > 1 and not self.place_free(self.player_two)):
            await self.game_over()
        
        # P1 eats apple
        if(self.apple.x == self.player_one.x and self.apple.y == self.player_one.y):
            self.player_one_score += 1
            self.p1_score_display.text = str(self.player_one_score)
            self.eat_apple(self.player_one)
            self.chime_state = "high"


        # P2 eats apple
        if(self.player_count > 1 and self.apple.x == self.player_two.x and self.apple.y == self.player_two.y):
            self.player_two_score += 1
            self.p2_score_display.text = str(self.player_two_score)
            self.eat_apple(self.player_two)
        # Pause for a moment
        return -1

    def eat_apple(self, player: Snake):
        asyncio.create_task(self.hardware.speaker.play_song_async(["C5","G5"], [8,8]))
        player.apple_eaten()
        if(self.player_one_score % 5 == 0 and self.max_wait > 100):
            self.max_wait -= 20
        self.apple.move_position()

    def restart(self):
        if(self.player_one_score > self.highscore):
            self.highscore = self.player_one_score
        self.player_one_score = 0
        self.player_two_score = 0
        self.max_wait = 300
        if(self.group != None):
            self.hardware.display.remove_element(self.group)
        del self.group
        del self.player_one
        if(self.player_count > 1):
            del self.player_two
        del self.apple
        print('Free memory before clean:', gc.mem_free())
        gc.collect()
        print('Free memory after clean:', gc.mem_free())
        self.hardware.display.reset()
        self.setup_screen()
        if(self.playing):
           self.hardware.blue_button.LED_off()
           self.hardware.joystick.debounce_time = .01
        else:
           self.hardware.blue_button.pulse()
           self.hardware.joystick.debounce_time = .5
        self.player_one = Snake(self.hardware.display, self.hardware.joystick, self, 1, self.group)
        if(self.player_count > 1):
            self.player_two = Snake(self.hardware.display, self.hardware.joystick, self, 2, self.group)
        self.apple = Apple(self.hardware.display, self, self.group)


    def place_free(self, obj, x_diff=0, y_diff=0):
        if(obj is not self.player_one):
            if(self.player_one.x == obj.x + x_diff and self.player_one.y == obj.y + y_diff):
                return False
        if(self.player_count > 1 and obj is not self.player_two):
            if(self.player_two.x == obj.x + x_diff and self.player_two.y == obj.y + y_diff):
                return False
        for tail in self.player_one.tails:
            if(obj.x + x_diff == tail.x and obj.y + y_diff == tail.y):
                return False
        if(self.player_count > 1):
            for tail in self.player_two.tails:
                if(obj.x + x_diff == tail.x and obj.y + y_diff == tail.y):
                    return False
        return True


    async def game_over(self):
        self.hardware.display.draw_text(25, 65, "Game Over!", 2, 0xFFFF00)
        asyncio.create_task(self.hardware.speaker.play_note_async("E2", 1))
        self.playing = False
        await asyncio.sleep(2.5)
        self.restart()


    def quit(self):
        pass