
import math
from hardware_controller import Hardware
from ponggame_data.paddle import Paddle
from ponggame_data.ball import Ball
import system_data.system_colors as colors
import time
import asyncio
from random import uniform
import adafruit_imageload
import displayio
from xyletic_game_engine.dynamic_object import DynamicObject

from xyletic_game_engine.game_engine import GameEngine
from xyletic_game_engine.game_object import GameObject
from xyletic_game_engine.vector_two import Vector2

game_start_x = 0
game_start_y = 18
game_width = 160
game_height = 110
paddle_width = 3
paddle_height = 18
paddle_speed = 5
ball_radius = 2.5
player_two_x = 150
player_one_x = 7

score_notes = ["G4", "A4", "G4", "A5"]

score_durations = [.15, .1, .15, .15]

class Center(Vector2):
    def __init__(self):
        x = round(game_width / 2 + game_start_x)
        y = round(game_height / 2 + game_start_y)
        self.height = 0
        super().__init__(x, y)

class PongGame(GameEngine):
    def __init__(self, hardware: Hardware) -> None:
        self.hardware = hardware
        self.playing = False
        self.blue_button = hardware.blue_button
        self.player_one_score = 0
        self.player_two_score = 0
        self.player_one_has_player = True
        self.player_two_has_player = False
        self.center = Center()
        super().__init__(25, hardware)
        self.image_load()
        self.hardware.display.reset()
        self.setup_screen()
        player_one_sprite = displayio.TileGrid(self.paddle_bitmap, pixel_shader=self.paddle_palette, x=player_one_x, y=round(game_height / 2 + game_start_y - paddle_height / 2))
        self.hardware.display.add_element(player_one_sprite)
        self.player_one = DynamicObject(player_one_x,
                                        round(game_height / 2 + game_start_y - paddle_height / 2),
                                        paddle_width,
                                        paddle_height,
                                        player_one_sprite,
                                          0, 90)
        player_two_sprite = displayio.TileGrid(self.paddle_bitmap, pixel_shader=self.paddle_palette, x=player_two_x, y=round(game_height / 2 + game_start_y - paddle_height / 2))
        self.hardware.display.add_element(player_two_sprite)
        self.player_two = DynamicObject(player_two_x,
                                        round(game_height / 2 + game_start_y - paddle_height / 2),
                                        paddle_width,
                                        paddle_height,
                                        player_two_sprite,
                                            0, 90)
        #set acceleration
        self.player_one.velocity.set_acceleration(1, 5)
        self.player_two.velocity.set_acceleration(1, 5)
        # self.player_one = Paddle(self.hardware.display, 1)
        # self.player_two = Paddle(self.hardware.display, 2)
        ball_sprite = displayio.TileGrid(self.ball_bitmap, pixel_shader=self.ball_palette, x=round(game_start_x + game_width/2 - ball_radius), y=round(game_start_y + game_height/2 - ball_radius + 1))
        self.hardware.display.add_element(ball_sprite)
        self.ball = DynamicObject(game_start_x + game_width/2 - ball_radius, game_start_y + game_height/2 - ball_radius + 1, ball_radius * 2, ball_radius * 2,
                                  ball_sprite,
                                    0, 0 + uniform(-20, 20) % 360)
        self.objects.append(self.ball)
        self.objects.append(self.player_one)
        self.objects.append(self.player_two)
        self.restart()

    def image_load(self):
        self.paddle_bitmap, self.paddle_palette = adafruit_imageload.load("/assets/pong/paddle.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        self.ball_bitmap, self.ball_palette = adafruit_imageload.load("/assets/pong/ball.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        self.background_bitmap, self.background_palette = adafruit_imageload.load("/assets/pong/pong-background.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)

    def setup_screen(self):
        # Graphic Setup
        self.hardware.display.draw_rect(0, 0, 160, game_start_y - 2, fill=colors.BLACK) # Background
        bg_sprite = displayio.TileGrid(self.background_bitmap, pixel_shader=self.background_palette, x=game_start_x, y=game_start_y)
        self.hardware.display.add_element(bg_sprite)
        self.p1_score_display = self.hardware.display.draw_text(64, 10, str(self.player_one_score), 1, 0xd53c6a) # Player 1 Score Value
        self.p2_score_display = self.hardware.display.draw_text(90, 10, str(self.player_two_score), 1, 0xd53c6a) # Player 2 Score Value
        # if(not self.playing):
        #     self.hardware.display.draw_text(5, 115, "Press", 1, colors.WHITE) # Score Label
        #     self.hardware.display.draw_text(41, 115, "blue", 1, colors.LIGHT_BLUE) # Score Label
        #     self.hardware.display.draw_text(70, 115, "to play!", 1, colors.WHITE) # Score Label


    def get_hardware_input(self) -> int:
        y = self.hardware.joystick.get_vertical()
        if(y < 300):
            return 270
        elif(y > 800):
            return 90
        return None


    async def process(self) -> int:
        if(self.hardware.menu_button.was_pressed()):
            return 0
        if self.playing:
            analog = self.hardware.joystick.get_vertical()
            dead_zone = 100
            center_value = 510
            soft_dead_zone = 30  # Range within which speed change is dampened

            if center_value + dead_zone >= analog >= center_value - dead_zone:
                self.player_one.velocity.decelerate()
            else:
                direction = 270 if analog < center_value else 90
                scale_factor = (center_value - analog) if analog < center_value else (analog - center_value)
                
                # Dampen the speed change if within the soft dead zone
                if scale_factor < soft_dead_zone:
                    scale_factor *= 0.5  # Reduce the speed change by half; adjust as needed

                # Calculate speed, ensuring it's within the range [0, max_speed]
                speed = min(self.player_one.velocity.max_speed, scale_factor / ((1023 - center_value) / self.player_one.velocity.max_speed))
                
                self.player_one.velocity.set_direction(direction)
                self.player_one.velocity.set_speed(speed)
        else:
            self.get_ai_direction(self.player_one)
            if(self.blue_button.is_pressed()):
                self.playing = True
                self.restart()
        
        self.get_ai_direction(self.player_two)
        await super().update()
        # change direction of ball if it hits the top or bottom of the screen
        if(self.ball.collision_box.y <= game_start_y or self.ball.collision_box.y >= game_start_y + game_height - ball_radius * 2):
            self.ball.velocity.set_direction(360 - self.ball.velocity.direction_angle)
            self.ball.collision_box.y = max(min(self.ball.collision_box.y, game_start_y + game_height - ball_radius * 2), game_start_y)
            asyncio.create_task(self.hardware.speaker.play_note_async("C5", .03))

        if(self.ball.check_collision(self.player_one)):
            self.ball.collision_box.x = player_one_x + paddle_width
            ball_center_y = self.ball.collision_box.y + ball_radius
            paddle_center_y = self.player_one.collision_box.y + paddle_height / 2
            y_diff = ball_center_y - paddle_center_y
            angle_variance = uniform(-5, 5) # Random variance between -5 and 5
            self.ball.velocity.set_direction((360 - (-y_diff / (paddle_height / 2) * 50) + angle_variance) % 360)
            asyncio.create_task(self.hardware.speaker.play_note_async("C4", .03))
        
        if(self.ball.check_collision(self.player_two)):
            self.ball.collision_box.x = player_two_x - ball_radius * 2
            ball_center_y = self.ball.collision_box.y + ball_radius
            paddle_center_y = self.player_two.collision_box.y + paddle_height / 2
            y_diff = ball_center_y - paddle_center_y
            angle_variance = uniform(-5, 5) # Random variance between -5 and 5
            self.ball.velocity.set_direction((180 - (y_diff / (paddle_height / 2) * 50) + angle_variance) % 360)
            asyncio.create_task(self.hardware.speaker.play_note_async("C4", .03))
            

        #prevent both paddles from going off screen
        if(self.player_one.collision_box.y <= game_start_y):
            self.player_one.collision_box.y = game_start_y
        elif(self.player_one.collision_box.y >= game_start_y + game_height - paddle_height):
            self.player_one.collision_box.y = game_start_y + game_height - paddle_height
        if(self.player_two.collision_box.y <= game_start_y):
            self.player_two.collision_box.y = game_start_y
        elif(self.player_two.collision_box.y >= game_start_y + game_height - paddle_height):
            self.player_two.collision_box.y = game_start_y + game_height - paddle_height
        

        if(self.ball.collision_box.x <= game_start_x - ball_radius * 2):
            asyncio.create_task(self.hardware.speaker.play_song_async(score_notes, score_durations))
            self.player_two_score += 1
            self.p2_score_display.text = str(self.player_two_score)
            self.ball.reset()
            self.ball.velocity.set_direction(0 + uniform(-20, 20) % 360)
            self.ball.velocity.set_speed(0)
            self.speed_increase_timer = time.monotonic()
        elif(self.ball.collision_box.x >= game_start_x + game_width):
            asyncio.create_task(self.hardware.speaker.play_song_async(score_notes, score_durations))
            self.player_one_score += 1
            self.p1_score_display.text = str(self.player_one_score)
            self.ball.reset()
            self.ball.velocity.set_direction(180 + uniform(-20, 20))
            self.ball.velocity.set_speed(0)
            self.speed_increase_timer = time.monotonic()
        
        if(self.player_one_score >= 10 or self.player_two_score >= 10):
            self.playing = False
            self.restart()
            await asyncio.sleep(1)
        
        if(time.monotonic() - self.speed_increase_timer > 2):
            self.speed_increase_timer = time.monotonic()
            if(self.ball.velocity.speed < 4):
                self.ball.velocity.set_speed(4)
            else:
                self.ball.velocity.set_speed(self.ball.velocity.speed + .15)
        
        #check if the ball direction is too close to vertical directions and then adjust it
        angle_dif = self.ball.velocity.direction_angle - 270
        if((angle_dif < 10 and angle_dif > -10) or (angle_dif > -190 and angle_dif < -170)):
            if(angle_dif < 0 or (angle_dif >= -180 and angle_dif < -170)):
                self.ball.velocity.set_direction(self.ball.velocity.direction_angle - 10)
            else:
                self.ball.velocity.set_direction(self.ball.velocity.direction_angle + 10)


        await self.draw()
        return -1
    
    async def draw(self):
        await super().draw()

    def handle_collision(self, player, player_x, direction_multiplier):
        self.ball.collision_box.x = player_x + (paddle_width if direction_multiplier == 1 else -ball_radius * 2)
        ball_center_y = self.ball.collision_box.y + ball_radius
        paddle_center_y = player.collision_box.y + paddle_height / 2
        y_diff = ball_center_y - paddle_center_y
        angle_variance = uniform(-5, 5) # Random variance between -5 and 5
        direction = (direction_multiplier * 180 - (y_diff / (paddle_height / 2) * 70) + angle_variance) % 360
        self.ball.velocity.set_direction(direction)
        asyncio.create_task(self.hardware.speaker.play_note_async("C4", .03))

    def get_ai_direction(self, player):
        target = None
        if player.collision_box.x == player_one_x and self.ball.velocity.x < 0:
            target = self.ball.collision_box
        elif player.collision_box.x == player_two_x and self.ball.velocity.x > 0:
            target = self.ball.collision_box
        else:
            target = self.center

        distance_to_target = (target.y + target.height / 2) - (player.collision_box.y + player.collision_box.height / 2)
        if(distance_to_target < 0):
            player.velocity.set_direction(270)
        elif(distance_to_target > 0):
            player.velocity.set_direction(90)
        distance_to_target = abs(distance_to_target)

        # Define a range near the target where the AI will slow down
        dampening_range = 10  # Adjust this value as needed

        if distance_to_target < dampening_range:
            dampened_speed = (distance_to_target / dampening_range) * player.velocity.max_speed
            player.velocity.set_speed(dampened_speed)
        else:
            player.velocity.accelerate()

    def restart(self):
        self.player_one_score = 0
        self.player_two_score = 0
        self.p1_score_display.text = str(self.player_one_score)
        self.p2_score_display.text = str(self.player_two_score)
        self.player_one.velocity.set_speed(0)
        self.player_two.velocity.set_speed(0)
        self.ball.reset()
        self.ball.velocity.set_direction(0 + uniform(-20, 20) % 360)
        self.ball.velocity.set_speed(0)
        #reset player y positions
        self.player_one.collision_box.y = round(game_height / 2 + game_start_y - paddle_height / 2)
        self.player_two.collision_box.y = round(game_height / 2 + game_start_y - paddle_height / 2)
        self.speed_increase_timer = time.monotonic()
        
        if(self.playing):
           self.blue_button.LED_off()
           self.hardware.joystick.debounce_time = .01
           self.player_two.velocity.set_acceleration(1, 4)
           self.player_one.velocity.set_acceleration(1, 6)
        else:
           self.blue_button.pulse()
           self.hardware.joystick.debounce_time = .5
           self.player_two.velocity.set_acceleration(1, 5)
           self.player_one.velocity.set_acceleration(1, 5)