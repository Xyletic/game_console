import analogio
import board
from xyletic_hardware.screen import Screen
import system_data.system_colors as colors
import asyncio


class Battery:
    def __init__(self, screen: Screen) -> None:
        self.adcpin = analogio.AnalogIn(board.VOLTAGE_MONITOR)
        self.__historical_values = []
        self.display = screen
        self.battery_state = "very high"
        self.battery_level = None
        

    def get_averaged_level(self):
        if(len(self.__historical_values) == 0):
            return 0
        avg = 0
        for v in self.__historical_values:
            avg += v
        return round(avg / len(self.__historical_values), 3)


    async def add_adc_reading(self):
        while True:
            self.__historical_values.append(round(self.adcpin.value * (3.3 / 65535) * 2.965, 3))
            while(len(self.__historical_values) > 20):
                self.__historical_values.pop(0)
            #self.voltage_display.text = str(self.get_averaged_level())
            level = self.get_averaged_level()
            #very high - 4.15 or above
            if(level > 4.15 and self.battery_state is not "very high"):
                self.battery_state = "very high"
                self.display.remove_element(self.battery_level)
                self.battery_level = self.display.draw_rect(142, 5, 11, 6, fill=colors.GREEN)
            #high - 3.95 - 4.05
            elif(level > 3.95 and level < 4.05 and self.battery_state is not "high"):
                self.battery_state = "high"
                self.display.remove_element(self.battery_level)
                self.battery_level = self.display.draw_rect(142, 5, 9, 6, fill=colors.LIME)
            #med - 3.7 - 3.85
            elif(level > 3.7 and level < 3.85 and self.battery_state is not "medium"):
                self.battery_state = "medium"
                self.display.remove_element(self.battery_level)
                self.battery_level = self.display.draw_rect(142, 5, 7, 6, fill=colors.YELLOW)
            #low - 3.4 - 3.6
            elif(level > 3.4 and level < 3.6 and self.battery_state is not "low"):
                self.battery_state = "low"
                self.display.remove_element(self.battery_level)
                self.battery_level = self.display.draw_rect(142, 5, 5, 6, fill=colors.ORANGE)
            #very low - 3.3 and below
            elif(level < 3.3 and self.battery_state is not "very low"):
                self.battery_state = "very low"
                self.display.remove_element(self.battery_level)
                self.battery_level = self.display.draw_rect(142, 5, 2, 6, fill=colors.RED)
            await asyncio.sleep(5)
        

    def show_battery(self):
        #self.display.draw_text(115, 10, "V:", 1, colors.WHITE)
        #self.voltage_display = self.display.draw_text(130, 10, str(self.get_averaged_level()), 1, colors.WHITE)
        self.display.draw_rect(140, 3, 15, 10, outline=colors.WHITE)
        self.battery_level = self.display.draw_rect(142, 5, 11, 6, fill=colors.GREEN)
        self.display.draw_rect(155, 6, 2, 4, fill=colors.WHITE)
        