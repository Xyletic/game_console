
import math
from hardware_controller import Hardware
from ponggame_data.paddle import Paddle
from ponggame_data.ball import Ball
import system_data.system_colors as colors
import time
import asyncio
from xyletic_game_engine.dynamic_object import DynamicObject

from xyletic_game_engine.game_engine import GameEngine
from xyletic_game_engine.game_object import GameObject
from xyletic_game_engine.vector_two import Vector2

game_start_x = 0
game_start_y = 18
game_width = 160
game_height = 110
paddle_width = 3
paddle_height = 15
paddle_speed = 5
ball_radius = 2
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
        self.restart()


    def setup_screen(self):
        # Graphic Setup
        self.hardware.display.draw_rect(0, 0, 160, game_start_y - 2, fill=colors.BLACK) # Background
        self.hardware.display.draw_rect(game_start_x, game_start_y, game_width, game_height, fill=0x3b2f2f) # Game Area
        self.hardware.display.draw_line(game_start_x, game_start_y - 1, game_width, game_start_y - 1, colors.WHITE) # Divider Line
        self.hardware.display.draw_text(5, 10, "P1:", 1, colors.WHITE) # Player 1 Score Label
        self.p1_score_display = self.hardware.display.draw_text(25, 10, str(self.player_one_score), 1, colors.WHITE) # Player 1 Score Value
        self.hardware.display.draw_text(50, 10, "P2:", 1, colors.WHITE) # Player 2 Score Label
        self.p2_score_display = self.hardware.display.draw_text(70, 10, str(self.player_two_score), 1, colors.WHITE) # Player 2 Score Value
        if(not self.playing):
            self.hardware.display.draw_text(5, 115, "Press", 1, colors.WHITE) # Score Label
            self.hardware.display.draw_text(41, 115, "blue", 1, colors.LIGHT_BLUE) # Score Label
            self.hardware.display.draw_text(70, 115, "to play!", 1, colors.WHITE) # Score Label


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
        dir = None
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
        await super().update()
        # change direction of ball if it hits the top or bottom of the screen
        if(self.ball.collision_box.y <= game_start_y or self.ball.collision_box.y >= game_start_y + game_height - ball_radius * 2):
            self.ball.velocity.set_direction(360 - self.ball.velocity.direction_angle)
            self.ball.collision_box.y = max(min(self.ball.collision_box.y, game_start_y + game_height - ball_radius * 2), game_start_y)
            asyncio.create_task(self.hardware.speaker.play_note_async("C5", .03))
        # change direction of ball if it hits the left or right of the screen
        if(self.ball.collision_box.x <= game_start_x or self.ball.collision_box.x >= game_start_x + game_width - ball_radius * 2):
            new_angle_deg = (180 - self.ball.velocity.direction_angle) % 360
            self.ball.velocity.set_direction(new_angle_deg)
            self.ball.collision_box.x = max(min(self.ball.collision_box.x, game_start_x + game_width - ball_radius * 2), game_start_x)
            asyncio.create_task(self.hardware.speaker.play_note_async("C4", .03))
        
        self.get_ai_direction(self.player_two)

        # await self.ball.move()
        # previous_ball_x = self.ball.x - self.ball.xspeed
        # # Check for player 2 collision
        # if(self.ball.xspeed > 0 
        #    and self.ball.x + ball_radius * 2 >= player_two_x #current position is greater or equal to paddle x
        #    and previous_ball_x + ball_radius * 2 <= player_two_x): #previous position is less than or equal to paddle x
            
        #     if(self.player_two.y <= self.ball.p2_intersection_y - ball_radius <= self.player_two.y + paddle_height
        #        or self.player_two.y <= self.ball.p2_intersection_y + ball_radius <= self.player_two.y + paddle_height):
        #         asyncio.create_task(self.hardware.speaker.play_note_async("C4", .03))
        #         self.ball.x = player_two_x - ball_radius * 2
        #         self.ball.collided_with_paddle(round(self.ball.p1_intersection_y))
        # # Check for player 1 collision
        # elif(self.ball.xspeed < 0
        #      and self.ball.x <= player_one_x + paddle_width #currnet position is less than or equal to paddle x
        #      and previous_ball_x >= player_one_x + paddle_width):#previous position is greater than or equal to paddle x
            
        #     if(self.player_one.y <= self.ball.p1_intersection_y - ball_radius <= self.player_one.y + paddle_height
        #        or self.player_one.y <= self.ball.p1_intersection_y + ball_radius <= self.player_one.y + paddle_height):
        #         asyncio.create_task(self.hardware.speaker.play_note_async("C4", .03))
        #         self.ball.x = player_one_x + paddle_width
        #         self.ball.collided_with_paddle(round(self.ball.p2_intersection_y))
        # if(self.ball.x <= game_start_x - ball_radius * 2):
        #     asyncio.create_task(self.hardware.speaker.play_song_async(score_notes, score_durations))
        #     self.player_two_score += 1
        #     self.p2_score_display.text = str(self.player_two_score)
        #     self.ball.reset()
        #     await asyncio.sleep(1)
        # elif(self.ball.x >= game_start_x + game_width):
        #     asyncio.create_task(self.hardware.speaker.play_song_async(score_notes, score_durations))
        #     self.player_one_score += 1
        #     self.p1_score_display.text = str(self.player_one_score)
        #     self.ball.reset()
        #     await asyncio.sleep(1)
        # self.ball.redraw()
        await self.draw()
        # await asyncio.sleep(.05)
        return -1
    
    async def draw(self):
        await super().draw()


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
        self.hardware.display.reset()
        self.setup_screen()
        if(self.playing):
           self.blue_button.LED_off()
           self.hardware.joystick.debounce_time = .01
        else:
           self.blue_button.pulse()
           self.hardware.joystick.debounce_time = .5
        self.player_one = DynamicObject(player_one_x,
                                        round(game_height / 2 + game_start_y - paddle_height / 2),
                                        paddle_width,
                                        paddle_height,
                                        self.hardware.display.draw_rect(player_one_x, round(game_height / 2 + game_start_y - paddle_height / 2),
                                                                        paddle_width, paddle_height, colors.WHITE), 0, 90)
        
        self.player_two = DynamicObject(player_two_x,
                                        round(game_height / 2 + game_start_y - paddle_height / 2),
                                        paddle_width,
                                        paddle_height,
                                        self.hardware.display.draw_rect(player_two_x, round(game_height / 2 + game_start_y - paddle_height / 2),
                                                                        paddle_width, paddle_height, colors.WHITE), 0, 90)
        #set acceleration
        self.player_one.velocity.set_acceleration(1, 5)
        self.player_two.velocity.set_acceleration(1, 5)
        # self.player_one = Paddle(self.hardware.display, 1)
        # self.player_two = Paddle(self.hardware.display, 2)
        self.ball = DynamicObject((game_start_x + game_width)/2, (game_start_y + game_height)/2, ball_radius * 2, ball_radius * 2, self.hardware.display.draw_circle(20, 20, ball_radius, colors.WHITE), 4, 45)
        self.objects.append(self.ball)
        self.objects.append(self.player_one)
        self.objects.append(self.player_two)
        pass