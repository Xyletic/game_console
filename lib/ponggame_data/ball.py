
from xyletic_hardware.buzzer import Buzzer
from xyletic_hardware.screen import Screen
import system_data.system_colors as colors
import ponggame_controller as game
import random
import time
import asyncio


class Ball:
    all_speed_choices = [-6,-5,-4,-3,-2,2,3,4,5,6]
    positive_speed_choices = [2,3,4,5,6]
    negative_speed_choices = [-2,-3,-4,-5,-6]
    def __init__(self, screen: Screen, speaker: Buzzer) -> None:
        self.display = screen
        self.speaker = speaker
        self.x = 77
        self.y = 52
        self.wall_hit_sound = 0
        self.xspeed = random.choice(Ball.all_speed_choices)
        self.yspeed = random.choice(Ball.all_speed_choices)
        self.ball_display = self.display.draw_circle(self.x, self.y, game.ball_radius, fill=colors.WHITE)

        #debug
        self.ball_intersect_visual = self.display.draw_circle(self.x, self.y, round(game.ball_radius / 2), fill=colors.RED)

        self.p1_intersection_y = -1
        self.p2_intersection_y = -1

    def calculate_slope(self):
        ball_slope = self.yspeed / self.xspeed
        ball_y_p1_intercept = (self.y + game.ball_radius) - ball_slope * (self.x + game.ball_radius * 2)
        ball_y_p2_intercept = (self.y + game.ball_radius) - ball_slope * self.x

        # calculate the y-coordinate of the intersection
        self.p1_intersection_y = ball_slope * (game.player_one_x + game.paddle_width) + ball_y_p1_intercept
        self.p2_intersection_y = ball_slope * (game.player_two_x) + ball_y_p2_intercept
        if(self.p1_intersection_y >= game.game_start_y and self.p1_intersection_y <= game.game_start_y + game.game_height and self.xspeed < 0):
            self.ball_intersect_visual.x = game.player_one_x + game.paddle_width
            self.ball_intersect_visual.y = round(self.p1_intersection_y)
        elif(self.p2_intersection_y >= game.game_start_y and self.p2_intersection_y <= game.game_start_y + game.game_height and self.xspeed > 0):
            self.ball_intersect_visual.x = game.player_two_x
            self.ball_intersect_visual.y = round(self.p2_intersection_y)
    

    async def move(self):
        if(self.wall_hit_sound != 0):
            elapsed_time = (time.monotonic() - self.wall_hit_sound) * 1000
            if(elapsed_time > 30):
                self.speaker.stop_playing()
                self.wall_hit_sound = 0
        self.x += self.xspeed
        self.y += self.yspeed
        if (self.y < game.game_start_y):
            self.wall_hit_sound = time.monotonic()
            asyncio.create_task(self.speaker.play_note_async("C5", .03))
            self.y = game.game_start_y
            self.yspeed *= -1
            self.calculate_slope()
        if (self.y > game.game_start_y + game.game_height - (game.ball_radius * 2)):
            self.wall_hit_sound = time.monotonic()
            asyncio.create_task(self.speaker.play_note_async("C5", .03))
            self.y = game.game_start_y + game.game_height - (game.ball_radius * 2)
            self.yspeed *= -1
            self.calculate_slope()
        

    def redraw(self):
        self.ball_display.x = self.x
        self.ball_display.y = self.y

    def collided_with_paddle(self, y_dif):
        if(self.xspeed < 0):
            self.xspeed = random.choice(Ball.positive_speed_choices)
        else:
            self.xspeed = random.choice(Ball.negative_speed_choices)
        if(y_dif < 0):
            self.yspeed = random.choice(Ball.negative_speed_choices)
        elif(y_dif > 0):
            self.yspeed = random.choice(Ball.positive_speed_choices)
        else:
            self.yspeed = random.choice(Ball.all_speed_choices)
        self.calculate_slope()



    def reset(self):
        self.x = 77
        self.y = 52
        self.xspeed = random.choice(Ball.all_speed_choices)
        self.yspeed = random.choice(Ball.all_speed_choices)
        self.calculate_slope()
        self.ball_display.x = self.x
        self.ball_display.y = self.y