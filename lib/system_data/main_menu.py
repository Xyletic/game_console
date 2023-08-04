from hardware_controller import Hardware
from system_data import sub_menu
from system_data.defined_shapes import draw_arrow
import system_data.system_colors as colors
import asyncio

class MainMenu:
    def __init__(self, title: str, hardware: Hardware, items: list[sub_menu.SubMenuItem]) -> None:
        self.title = title
        self.hardware = hardware
        self.hardware.joystick.debounce_time = .1
        self.menu_items = items
        self.__highlighted = 0
        self.text_items = []
        self.create_and_show()
        

    def create_and_show(self):
        self.hardware.display.reset()
        self.text_items = []
        self.group = self.hardware.display.create_group()
        # Background
        self.hardware.display.draw_rect(0, 20, 160, 108, fill=colors.DARK_GRAY, group=self.group)
        self.hardware.display.draw_rect(0, 0, 160, 20, fill=colors.BLACK, group=self.group)
        # Title, do some basic math to approximate centering the text
        self.hardware.display.draw_text((int)(80 - (len(self.title) / 2) * 6), 12, self.title, 1, colors.WHITE, group=self.group)
        self.highlighter = self.hardware.display.draw_rect(3, 23 + (20 * self.__highlighted), 150, 16, colors.LIGHT_GRAY, None, 1, self.group)
        self.arrow = draw_arrow(8, 28 + (20 * self.__highlighted), self.hardware.display, self.group)
        # Items
        for i, item in enumerate(self.menu_items):
            self.show_menu_item(item, i == self.__highlighted, pos=i)

    def show_menu_item(self, item: sub_menu.SubMenuItem, highlighted: bool, pos: int): 
        if(highlighted):
            self.text_items.append(self.hardware.display.draw_text(20, 31 + (20 * pos), item.name, 1, colors.BLACK, group=self.group))
        else:
            self.text_items.append(self.hardware.display.draw_text(20, 31 + (20 * pos), item.name, 1, colors.WHITE, group=self.group))

    async def process(self) -> int:
        v = self.hardware.joystick.get_last_y_direction()
        b = self.hardware.green_button.is_pressed()
        if(b):
            return self.__highlighted
        if(v == 270):
            if(self.__highlighted == 0):
                self.set_highlighted(len(self.menu_items) - 1)
            else:
                self.set_highlighted(self.__highlighted - 1)
        elif(v == 90):
            if(self.__highlighted == len(self.menu_items) - 1):
                self.set_highlighted(0)
            else:
                self.set_highlighted(self.__highlighted + 1)
        await asyncio.sleep(.1)
        return -1

    def set_highlighted(self, value):
        self.text_items[self.__highlighted].color = colors.WHITE
        self.text_items[value].color = colors.BLACK
        self.hardware.display.remove_element(self.arrow, self.group)
        self.highlighter.y = 23 + (20 * value)
        self.arrow = draw_arrow(8, 28 + (20 * value), self.hardware.display, self.group)
        self.__highlighted = value
        self.hardware.display.update()

    def remove(self):
        self.hardware.display.remove_element(self.group)