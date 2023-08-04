from adafruit_bus_device.i2c_device import I2CDevice
import time
import microcontroller

ID = 0x00
FIRMWARE_MINOR = 0x01
FIRMWARE_MAJOR = 0x02
BUTTON_STATUS = 0x03
INTERRUPT_CONFIG = 0x04
BUTTON_DEBOUNCE_TIME = 0x05
PRESSED_QUEUE_STATUS = 0x07
PRESSED_QUEUE_FRONT = 0x08
PRESSED_QUEUE_BACK = 0x0C
CLICKED_QUEUE_STATUS = 0x10
CLICKED_QUEUE_FRONT = 0x11
CLICKED_QUEUE_BACK = 0x15
LED_BRIGHTNESS = 0x19
LED_PULSE_GRANULARITY = 0x1A
LED_PULSE_CYCLE_TIME = 0x1B
LED_PULSE_OFF_TIME = 0x1D
I2C_ADDRESS = 0x1F

class Button:

    def set_brightness(self, level, save=True):
        self.__brightness = int(level * 255 / 100)
        if save:
            microcontroller.nvm[2:3] = level.to_bytes(1, 'big')
        self.LED_on()

    def get_brightness(self):
        return int(self.__brightness / 255  * 100)

    def init_brightness(self):
        try:
            self.__brightness = int(int.from_bytes(microcontroller.nvm[2:3], 'big') * 255 / 100)
        except:
            self.set_brightness(50)

    def __init__(self, i2c, addr=0x6F) -> None:
        self.__brightness = -1
        if(self.__brightness == -1):
            self.init_brightness()
        self.device = I2CDevice(i2c, addr)
        # Test LED
        self.LED_on()
        time.sleep(.2)
        self.LED_off()


    def __getByte(self, buffer):
        with self.device as i2c:
            i2c.write(bytes([buffer]))
            result = bytearray(1)
            i2c.readinto(result)
            return int.from_bytes(result, 'big')


    def __writeByte(self, buffer, value):
        with self.device as i2c:
            i2c.write(bytes([buffer, value]))


    def __writeWord(self, buffer, value):
        with self.device as i2c:
            i2c.write(bytes([buffer, value & 0xFF, (value >> 8) & 0xFF]))


    def is_pressed(self):
        button_status = self.__getByte(BUTTON_STATUS)
        is_pressed = (button_status & ~(0xFB)) >> 2
        return bool(is_pressed)
    

    def __setLED(self, brightness, cycle_time, off_time, granularity = 1):
        self.__writeByte(LED_BRIGHTNESS, brightness)
        self.__writeWord(LED_PULSE_CYCLE_TIME, cycle_time)
        self.__writeWord(LED_PULSE_OFF_TIME, off_time)
        self.__writeByte(LED_PULSE_GRANULARITY, granularity)


    def LED_off(self):
        self.__setLED(0, 0, 0)

    
    def pulse(self):
        self.__setLED(self.__brightness, 2000, 2000, 1)


    def LED_on(self):
        self.__setLED(self.__brightness, 0, 0)