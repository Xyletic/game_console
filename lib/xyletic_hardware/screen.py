import pwmio
import board
import busio
import displayio
import digitalio
import storage
import sdcardio
import terminalio
import microcontroller
from adafruit_display_shapes import circle, rect, polygon, line
from adafruit_display_text.label import Label
from adafruit_st7735r import ST7735R

class Screen:
    def __init__(self) -> None:
        displayio.release_displays()
        spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP16)  # SPI setup
        self.__brightness = pwmio.PWMOut(board.GP15, frequency=5000, duty_cycle=0)
        tft_cs = board.GP17
        tft_dc = board.GP22
        card_cs = board.GP21
        reset = board.GP20

        # SD Card
        sdcard = sdcardio.SDCard(spi, card_cs)
        vfs = storage.VfsFat(sdcard)
        storage.mount(vfs, "/sd")

        # Display
        try:
            self.set_brightness(int.from_bytes(microcontroller.nvm[0:1], 'big'), False)
        except:
            self.set_brightness(50)
        self.display_bus = displayio.FourWire(
            spi, command=tft_dc, chip_select=tft_cs, reset=reset
        )
        self.display_bus.reset()
        self.display = ST7735R(self.display_bus, width=160, height=128, rotation=90, bgr=True)
        self.__main_group = displayio.Group()
        self.display.show(self.__main_group)
        self.showing_battery = False
        

    def set_brightness(self, level, save=True):
        self.__brightness.duty_cycle = int(level * 65535 / 100)
        if save:
            microcontroller.nvm[0:1] = level.to_bytes(1, 'big')

    def get_brightness(self):
        return int(self.__brightness.duty_cycle / 65535  * 100)

    def create_group(self):
        new_group = displayio.Group()
        self.__main_group.append(new_group)
        return new_group
    
    def draw_polygon(self, points: list[tuple[int, int]], outline = None, close = None, colors=None, group=None):
        render = polygon.Polygon(points, outline=outline, close=close, colors=colors)
        if(group is None):
            self.__main_group.append(render)
        else:
            group.append(render)
        return render

    def draw_text(self, text_x, text_y, text_str, scale_size, text_color, group=None):
        render = Label(terminalio.FONT, text=text_str, color=text_color)
        if(group is None):
            text_group = displayio.Group(scale=scale_size, x=text_x, y=text_y)
            text_group.append(render)
            self.__main_group.append(text_group)
            return render
        else:
            text_group = displayio.Group(scale=scale_size, x=text_x, y=text_y)
            text_group.append(render)
            group.append(text_group)
        return render

    def draw_rect(self, x, y, w, h, fill=None, outline=None, stroke=1, group=None):
        render = rect.Rect(x, y, w, h, fill = fill, outline = outline, stroke = stroke)
        if(group is None):
            self.__main_group.append(render)
        else:
            group.append(render)
        return render

    def draw_line(self, x1, y1, x2, y2, color, group=None):
        render = line.Line(x1, y1, x2, y2, color)
        if(group is None):
            self.__main_group.append(render)
        else:
            group.append(render)
        return render
    
    def draw_circle(self, x, y, radius, fill=None, outline=None, stroke=1, group=None):
        render = circle.Circle(x, y, radius, fill=fill, outline=outline, stroke=stroke)
        if(group is None):
            self.__main_group.append(render)
        else:
            group.append(render)
        return render
    
    def reset(self):
        self.__main_group = displayio.Group()
        self.display.show(self.__main_group)
        self.showing_battery = False

    
    def update(self):
        self.display.refresh()

    def remove_element(self, element, group=None):
        if(group is None):
            self.__main_group.remove(element)
        else:
            group.remove(element)
    
    def add_element(self, element, group=None):
        if(group is None):
            self.__main_group.append(element)
        else:
            group.append(element)