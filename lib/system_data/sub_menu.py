
from hardware_controller import Hardware
from system_data.defined_shapes import draw_arrow
import system_data.system_colors as colors
import time

class SubMenuItem:
    def __init__(self, name) -> None:
        self.name = name

class SliderMenu:
    def __init__(self, title: str, subtitle: str, hardware: Hardware, initial_value: int, function) -> None:
        self.title = title
        self.subtitle = subtitle
        self.hardware = hardware
        self.value = initial_value
        self.func = function
        self.moveable_bar = None
        self.create_and_show()

    def create_and_show(self):
        self.hardware.display.reset()
        self.group = self.hardware.display.create_group()
        # Background
        self.hardware.display.draw_rect(0, 20, 160, 108, fill=colors.DARK_GRAY, group=self.group)
        self.hardware.display.draw_rect(0, 0, 160, 20, fill=colors.BLACK, group=self.group)
        # Title, do some basic math to approximate centering the text
        self.hardware.display.draw_text((int)(80 - (len(self.title) / 2) * 6), 12, self.title, 1, colors.WHITE, group=self.group)
        self.hardware.display.draw_text((int)(80 - (len(self.subtitle) / 2) * 6), 31, self.subtitle, 1, colors.WHITE, group=self.group)
        # Slider bar
        self.hardware.display.draw_rect(30, 42, 100, 21, fill=colors.BLACK, outline=colors.WHITE, group=self.group)
        if self.__get_value_display_width() > 0:
            self.moveable_bar = self.hardware.display.draw_rect(32, 44, self.__get_value_display_width(), 17, fill=colors.LIGHT_GRAY, outline=colors.LIGHTER_GRAY, group=self.group)
        # Back (highlighted)
        self.hardware.display.draw_rect(15, 94, 130, 16, colors.LIGHT_GRAY, None, 1, self.group)
        self.hardware.display.draw_text(35, 102, "Back", 1, colors.BLACK, group=self.group)
        self.arrow = draw_arrow(23, 99, self.hardware.display, self.group)

    def adjust_value(self, new_value: int):
        if(new_value > 100):
            new_value = 100
        if(new_value < 0):
            new_value = 0
        if(self.value == new_value):
            return
        self.value = new_value
        self.func(self.value)
        temp = self.moveable_bar
        if(self.__get_value_display_width() > 0):
            self.moveable_bar = self.hardware.display.draw_rect(32, 44, self.__get_value_display_width(), 17, fill=colors.LIGHT_GRAY, outline=colors.LIGHTER_GRAY, group=self.group)
        else:
            self.moveable_bar = None
        if temp is not None:
            self.hardware.display.remove_element(temp, self.group)
                                                                                             
    def process(self) -> int:
        h = self.hardware.joystick.get_horizontal()
        b = self.hardware.green_button.is_pressed()
        if(b):
            return 0
        if(h < 300):
            self.adjust_value(self.value - 5)
        elif(h > 800):
            self.adjust_value(self.value + 5)
        time.sleep(.1)
        return -1


    def __get_value_display_width(self):
        return int(self.value / 100  * 96)

    def remove(self):
        self.hardware.display.remove_element(self.group)