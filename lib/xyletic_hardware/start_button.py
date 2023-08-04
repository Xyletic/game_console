import asyncio
import digitalio
import time

class StartButton:
    def __init__(self, pin, debounce_time=0.02, timeout=1):
        self.button = digitalio.DigitalInOut(pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP
        self.debounce_time = debounce_time
        self.button_state = self.button.value
        self.last_changed = time.monotonic()
        self.pressed = False
        self.press_time = self.last_changed
        self.timeout = timeout

    async def watcher(self):
        while True:
            self.update()
            if self.is_pressed():
                self.press_time = time.monotonic()
                self.pressed = True
            await asyncio.sleep(self.debounce_time)

    def update(self):
        now = time.monotonic()
        current_state = self.button.value
        if current_state != self.button_state and (now - self.last_changed) > self.debounce_time:
            self.button_state = current_state
            self.last_changed = now

    def is_pressed(self):
        return not self.button_state

    def was_pressed(self):
        if self.pressed and time.monotonic() - self.press_time <= self.timeout:
            self.pressed = False
            return True
        return False
