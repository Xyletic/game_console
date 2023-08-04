import hardware_controller
import system_controller
import battery_monitor
import asyncio
import gc

print()
print('Starting free memory:', gc.mem_free())

hardware = hardware_controller.Hardware()
battery = battery_monitor.Battery(hardware.display)
system = system_controller.System(hardware, battery)


async def main_kick_off():
    sys = asyncio.create_task(system.system_process())
    bat = asyncio.create_task(battery.add_adc_reading())
    mb = asyncio.create_task(hardware.menu_button.watcher())
    joy = asyncio.create_task(hardware.joystick.watcher())
    await asyncio.gather(sys, bat, mb, joy) 


asyncio.run(main_kick_off())