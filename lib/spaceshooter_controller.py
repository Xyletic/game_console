from spaceshooter_data.basic_enemy import BasicEnemy
from spaceshooter_data.player import PlayerShip
from spaceshooter_data.player_laser import PlayerLaser
from spaceshooter_data.star import Star
from hardware_controller import Hardware
import system_data.system_colors as colors
import adafruit_imageload
import displayio
import time
import asyncio

game_start_x = 0
game_start_y = 18
game_width = 160
game_height = 110
player_speed = 3
enemy_speed = 2
laser_speed = 9
laser_damage = 1

laser_notes = ["G7", "A5"]
laser_notes_durations = [.05, .05]


class SpaceGame:
    def __init__(self, hardware: Hardware) -> None:
        self.hardware = hardware
        self.bitmap, self.primary_palette = adafruit_imageload.load("/assets/spaceshooter/enemy_ship.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        self.hit_palette = displayio.Palette(len(self.primary_palette))
        for i, color in enumerate(self.primary_palette):
            if(color != 0):
                self.hit_palette[i] = 0xFFFFFF
        self.primary_palette.make_transparent(0)
        self.hit_palette.make_transparent(0)
        self.playing = False
        self.group = None
        self.stars = []
        self.player_lasers = []
        self.enemies = []
        self.laser_delay = .25
        self.last_laser = time.monotonic()
        self.last_enemy_spawn = time.monotonic()
        self.enemy_delay = 1
        self.restart()



    def setup_screen(self):
        self.hardware.display.reset()
        self.group = self.hardware.display.create_group()
        self.hardware.display.draw_rect(0, 0, 160, 128, fill=colors.BLACK, group=self.group) # Background
        self.hardware.display.draw_line(game_start_x, game_start_y - 1, game_width, game_start_y - 1, colors.WHITE, group=self.group) # Divider Line
        for _ in range(5):
            self.stars.append(Star(self.hardware.display, self.group))
        

    async def process(self):
        if(self.hardware.menu_button.was_pressed()):
            return 0
        for e in self.enemies:
            if(e.health <= 0):
                e.remove()
                self.enemies.remove(e)
        if(time.monotonic() - self.last_enemy_spawn >= self.enemy_delay):
            self.enemies.append(BasicEnemy(self.group, self.bitmap, self.primary_palette, self.hit_palette))
            self.last_enemy_spawn = time.monotonic()
        for l in self.player_lasers:
            l.move()
            if(l.sprite.x > game_start_x + game_width):
                l.remove()
                self.player_lasers.remove(l)
                del l
                continue
            for e in self.enemies:
                if(l.is_colliding(e.sprite.x, e.sprite.y, 
                        e.sprite.x + e.get_width(),
                        e.sprite.y + e.get_height())):
                    l.remove()
                    self.player_lasers.remove(l)
                    del l
                    asyncio.create_task(self.hardware.speaker.play_note_async("F4", .03))
                    asyncio.create_task(e.hit(laser_damage))
                    break
        if(self.playing):
            x = self.hardware.joystick.get_last_x_direction()
            y = self.hardware.joystick.get_last_y_direction()
            self.player.move(x, y)
        else:
            self.player.bounce()
        for e in self.enemies:
            e.move()

        
        if(time.monotonic() - self.last_laser > self.laser_delay):
            self.player_lasers.append(PlayerLaser(self.player.get_front(), self.player.get_center(), self.hardware.display, self.group))
            self.last_laser = time.monotonic()
            asyncio.create_task(self.hardware.speaker.play_song_async(laser_notes, laser_notes_durations))
        for star in self.stars:
            star.move()
        #gc.collect()
        await asyncio.sleep(.03)
        return -1


    def restart(self):
        self.stars = []
        self.setup_screen()
        if(self.playing):
            self.hardware.joystick.debounce_time = .02
        else:
            self.hardware.joystick.debounce_time = .5
        self.enemies = [BasicEnemy(self.group, self.bitmap, self.primary_palette, self.hit_palette)]
        self.player = PlayerShip(self.group)