

from hardware_controller import Hardware
import asyncio
import time

class GameEngine:
    def __init__(self, updates_per_second: int, hardware: Hardware) -> None:
        self.updates_per_second = updates_per_second
        self.hardware = hardware
        self.objects = []
        self.hudobjects = []
        self.delta_time = 0
        self.time_watcher = time.monotonic()
        pass

    def start(self):
        pass

    async def update(self):
        # Set delta time and reset time watcher
        self.delta_time = time.monotonic() - self.time_watcher
        self.time_watcher = time.monotonic()

        # Handle input

        # Update all objects
        for obj in self.objects:
            obj.update(self.delta_time)
        # Update logic
        for hud in self.hudobjects:
            hud.update(self.delta_time)
        
        

    async def draw(self):
        # send draw command to all objects
        for obj in self.objects:
            obj.draw()
        # update HUD
        for hud in self.hudobjects:
            hud.draw()
        # Pause for any remaining time left in the update based on the updates per second and the time it took to update
        await asyncio.sleep(max(0, 1 / self.updates_per_second - (time.monotonic() - self.time_watcher)))
        
