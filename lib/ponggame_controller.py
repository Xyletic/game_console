
from hardware_controller import Hardware
from ponggame_data.paddle import Paddle
from ponggame_data.ball import Ball
import system_data.system_colors as colors
import time
import asyncio

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

class Center:
    y = round(game_height / 2 + game_start_y - paddle_height / 2)

class PongGame:
    def __init__(self, hardware: Hardware) -> None:
        self.hardware = hardware
        self.playing = False
        self.blue_button = hardware.blue_button
        self.player_one_score = 0
        self.player_two_score = 0
        self.player_one_has_player = True
        self.player_two_has_player = False
        self.restart()


    def setup_screen(self):
        # Graphic Setup
        self.hardware.display.draw_rect(0, 0, 160, 128, fill=colors.BLACK) # Background
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
        return 0


    async def process(self) -> int:
        if(self.hardware.menu_button.was_pressed()):
            return 0
        dir = 0
        if(self.playing):
            dir = self.hardware.joystick.get_last_direction()
        else:
            dir = self.get_ai_direction(self.player_one)
            if(self.blue_button.is_pressed()):
                self.playing = True
                self.restart()
        self.player_one.move(dir)
        dir = self.get_ai_direction(self.player_two)
        self.player_two.move(dir)
        await self.ball.move()
        previous_ball_x = self.ball.x - self.ball.xspeed
        # Check for player 2 collision
        if(self.ball.xspeed > 0 
           and self.ball.x + ball_radius * 2 >= player_two_x #current position is greater or equal to paddle x
           and previous_ball_x + ball_radius * 2 <= player_two_x): #previous position is less than or equal to paddle x
            
            if(self.player_two.y <= self.ball.p2_intersection_y - ball_radius <= self.player_two.y + paddle_height
               or self.player_two.y <= self.ball.p2_intersection_y + ball_radius <= self.player_two.y + paddle_height):
                asyncio.create_task(self.hardware.speaker.play_note_async("C4", .03))
                self.ball.x = player_two_x - ball_radius * 2
                self.ball.collided_with_paddle(round(self.ball.p1_intersection_y))
        # Check for player 1 collision
        elif(self.ball.xspeed < 0
             and self.ball.x <= player_one_x + paddle_width #currnet position is less than or equal to paddle x
             and previous_ball_x >= player_one_x + paddle_width):#previous position is greater than or equal to paddle x
            
            if(self.player_one.y <= self.ball.p1_intersection_y - ball_radius <= self.player_one.y + paddle_height
               or self.player_one.y <= self.ball.p1_intersection_y + ball_radius <= self.player_one.y + paddle_height):
                asyncio.create_task(self.hardware.speaker.play_note_async("C4", .03))
                self.ball.x = player_one_x + paddle_width
                self.ball.collided_with_paddle(round(self.ball.p2_intersection_y))
        if(self.ball.x <= game_start_x - ball_radius * 2):
            asyncio.create_task(self.hardware.speaker.play_song_async(score_notes, score_durations))
            self.player_two_score += 1
            self.p2_score_display.text = str(self.player_two_score)
            self.ball.reset()
            await asyncio.sleep(1)
        elif(self.ball.x >= game_start_x + game_width):
            asyncio.create_task(self.hardware.speaker.play_song_async(score_notes, score_durations))
            self.player_one_score += 1
            self.p1_score_display.text = str(self.player_one_score)
            self.ball.reset()
            await asyncio.sleep(1)
        self.ball.redraw()
        await asyncio.sleep(.05)
        return -1


    def get_ai_direction(self, player: Paddle) -> int:
        target = None
        if(player.x == player_one_x and self.ball.xspeed < 0):
            target = self.ball
        elif(player.x == player_two_x and self.ball.xspeed > 0):
            target = self.ball
        else:
            target = Center
        if(target.y < player.y + 5):
            return 270
        elif(target.y > player.y + 9):
            return 90
        return 0

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
        self.player_one = Paddle(self.hardware.display, 1)
        self.player_two = Paddle(self.hardware.display, 2)
        self.ball = Ball(self.hardware.display, self.hardware.speaker)
        pass