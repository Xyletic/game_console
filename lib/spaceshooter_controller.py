from spaceshooter_data.star import Star
from hardware_controller import Hardware
import system_data.system_colors as colors
import time
import asyncio

game_start_x = 0
game_start_y = 18
game_width = 160
game_height = 110

notes = ['G4', 'A4', 'B4', 'D5', 'D5', 'B4', 'A4', 'G4', 'E4', 'G4', 'A4', 'B4', 'A4', 'B4', 'D5']
durations = [2, 4, 8, 2, 4, 4, 4, 8, 4, 4, 4, 8, 4, 4, 8] # note durations, now in quarter and eighth notes




class SpaceGame:
    def __init__(self, hardware: Hardware) -> None:
        self.hardware = hardware
        self.playing = False
        self.group = None
        self.stars = []
        self.restart()

    async def play_song(self):
        await self.hardware.speaker.play_song_async(notes, durations)

    def setup_screen(self):
        self.hardware.display.reset()
        self.group = self.hardware.display.create_group()
        self.hardware.display.draw_rect(0, 0, 160, 128, fill=colors.BLACK, group=self.group) # Background
        self.hardware.display.draw_line(game_start_x, game_start_y - 1, game_width, game_start_y - 1, colors.WHITE, group=self.group) # Divider Line
        for i in range(20):
            self.stars.append(Star(self.hardware.display, self.group))
        

    async def process(self):
        if(self.hardware.menu_button.was_pressed()):
            return 0
        for star in self.stars:
            star.move()
        await asyncio.sleep(.05)
        return -1


    def restart(self):
        self.stars = []
        self.setup_screen()
        