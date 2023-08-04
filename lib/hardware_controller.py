import board
import busio
from lib.xyletic_hardware import joystick, button, screen, buzzer, start_button

class Hardware:
    def __init__(self) -> None:
        i2c = busio.I2C(board.GP5, board.GP4)
        self.joystick = joystick.Joystick(i2c)
        self.green_button = button.Button(i2c, 0x6F)
        self.blue_button = button.Button(i2c, 0x6E)
        self.white_button = button.Button(i2c, 0x6D)
        self.red_button = button.Button(i2c, 0x6B)
        self.menu_button = start_button.StartButton(board.GP14)
        self.speaker = buzzer.Buzzer()
        self.display = screen.Screen()
        self.all_LEDs_off()

    def all_LEDs_off(self):
        self.green_button.LED_off()
        self.blue_button.LED_off()
        self.red_button.LED_off()
        self.white_button.LED_off()