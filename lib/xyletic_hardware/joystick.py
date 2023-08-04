from adafruit_bus_device.i2c_device import I2CDevice
import time
import asyncio

JOYSTICK_ID             = 0x00
JOYSTICK_VERSION1       = 0x01
JOYSTICK_VERSION2       = 0x02
JOYSTICK_X_MSB          = 0x03
JOYSTICK_X_LSB          = 0x04
JOYSTICK_Y_MSB          = 0x05
JOYSTICK_Y_LSB          = 0x06
JOYSTICK_BUTTON         = 0x07
JOYSTICK_STATUS         = 0x08
JOYSTICK_I2C_LOCK       = 0x09
JOYSTICK_CHANGE_ADDREESS= 0x0A

class Joystick:
    def __init__(self, i2c, debounce_time=.1, timeout=1) -> None:
        self.device = I2CDevice(i2c, 0x20)
        self.debounce_time = debounce_time
        self.button_state = self.__get_button()
        self.last_changed = time.monotonic()
        self.pressed = False
        self.press_time = self.last_changed
        self.timeout = timeout
        self.last_x_val = -1
        self.last_y_val = -1
        self.last_x_update = time.monotonic()
        self.last_y_update = time.monotonic()
        

    def __getByte(self, buffer):
        with self.device as i2c:
            i2c.write(bytes([buffer]))
            result = bytearray(1)
            i2c.readinto(result)
            return int.from_bytes(result, 'big')

    def get_horizontal(self):
        msb = self.__getByte(JOYSTICK_X_MSB)
        lsb = self.__getByte(JOYSTICK_X_LSB)
        return 1023 - (((msb << 8) | lsb) >> 6)
    
    def get_vertical(self):
        msb = self.__getByte(JOYSTICK_Y_MSB)
        lsb = self.__getByte(JOYSTICK_Y_LSB)
        return 1023 - (((msb << 8) | lsb) >> 6)


    async def watcher(self):
        while True:
            self.update()
            if self.is_pressed():
                self.press_time = time.monotonic()
                self.pressed = True
            await asyncio.sleep(self.debounce_time)


    def update(self):
        now = time.monotonic()
        current_button_state = self.__get_button()
        current_x_axis = self.get_horizontal()
        current_y_axis = self.get_vertical()

        if current_button_state != self.button_state and (now - self.last_changed) > self.debounce_time:
            self.button_state = current_button_state
            self.last_changed = now

        if current_x_axis > 800 and (now - self.last_x_update) > self.debounce_time:
            self.last_x_val = 0  # Right
            self.last_x_update = now

        elif current_x_axis < 300 and (now - self.last_x_update) > self.debounce_time:
            self.last_x_val = 180  # Left
            self.last_x_update = now

        if current_y_axis > 800 and (now - self.last_y_update) > self.debounce_time:
            self.last_y_val = 90  # Down
            self.last_y_update = now

        elif current_y_axis < 300 and (now - self.last_y_update) > self.debounce_time:
            self.last_y_val = 270  # Up
            self.last_y_update = now
            
    def get_last_direction(self):
        now = time.monotonic()
        if now - self.last_x_update <= self.timeout and now - self.last_y_update <= self.timeout:
            result = self.last_x_val if self.last_x_update > self.last_y_update else self.last_y_val
        elif now - self.last_x_update <= self.timeout:
            result = self.last_x_val
        elif now - self.last_y_update <= self.timeout:
            result = self.last_y_val
        else:
            result = -1

        self.last_x_val = -1
        self.last_y_val = -1
        return result

    def get_last_x_direction(self):
        result = self.last_x_val if time.monotonic() - self.last_x_update <= self.timeout else -1
        self.last_x_val = -1
        return result

    def get_last_y_direction(self):
        result = self.last_y_val if time.monotonic() - self.last_y_update <= self.timeout else -1
        self.last_y_val = -1
        return result
        
    
    def __get_button(self):
        return self.__getByte(JOYSTICK_BUTTON)
    
    def is_pressed(self):
        return not self.button_state
    
    def was_pressed(self):
        if self.pressed and time.monotonic() - self.press_time <= self.timeout:
            self.pressed = False
            return True
        return False