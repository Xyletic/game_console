import os
import microcontroller
from hardware_controller import Hardware
from system_data.sub_menu import SubMenuItem, SliderMenu
import snakegame_controller
import spaceshooter_controller
import ponggame_controller
import system_data.main_menu as menu

class System:
    def __init__(self, hardware: Hardware, battery) -> None:
        self.hardware = hardware
        self.battery = battery
        self.state = "mainmenu"
        stat = os.statvfs("/")
        free = stat[0] * stat[3]
        free_kb = free / 1024  # Convert bytes to kilobytes
        print()
        print("System stats:")
        print("Available flash memory:", round(free_kb, 2), "KB")
        print(f"CPU 0 temp: {round(microcontroller.cpus[0].temperature,1)} °C")
        print(f"CPU 1 temp: {round(microcontroller.cpus[1].temperature,1)} °C")
        print("CPU 0 freq:", microcontroller.cpus[0].frequency / 1000000, "MHz")
        print("CPU 1 freq:", microcontroller.cpus[1].frequency / 1000000, "MHz")
        reset_reason = microcontroller.cpu.reset_reason
        if reset_reason == microcontroller.ResetReason.POWER_ON:
            print("Reset Reason: Power On.")
        elif reset_reason == microcontroller.ResetReason.BROWNOUT:
            print("Reset Reason: Brownout.")
        elif reset_reason == microcontroller.ResetReason.WATCHDOG:
            print("Reset Reason: Watchdog.")
        elif reset_reason == microcontroller.ResetReason.SOFTWARE:
            print("Reset Reason: Software.")
        elif reset_reason == microcontroller.ResetReason.RESET_PIN:
            print("Reset Reason: Reset Pin.")
        elif reset_reason == microcontroller.ResetReason.RESCUE_DEBUG:
            print("Reset Reason: Rescue Debug.")
        elif reset_reason == microcontroller.ResetReason.UNKNOWN:
            print("Reset Reason: Unknown.")
        else:
            print("Reset Reason: Undefined.")
        print()
        self.slider_menu = None
        self.sub_menu = None
        self.process = self.get_main_menu()


    async def system_process(self):
        while True: # Main "System" loop
            if(self.state == "mainmenu"):
                decision = await self.process.process()
                if(decision == -1):
                    pass
                elif(decision == 0):
                    self.process = ponggame_controller.PongGame(self.hardware)
                    self.state = "playing"
                elif(decision == 1):
                    self.process = snakegame_controller.SnakeGame(self.hardware)
                    self.state = "playing"
                elif(decision == 2):
                    self.process = spaceshooter_controller.SpaceGame(self.hardware)
                    #asyncio.create_task(process.play_song())
                    self.state = "playing"
                elif(decision == 3):
                    self.process = self.get_settings_menu()
                    self.state = "settingsmenu"
            elif(self.state == "playing"):
                decision = await self.process.process()
                if(decision == None or decision == -1):
                    pass
                elif(decision == 0):
                    self.state = "pausemenu"
                    self.hardware.all_LEDs_off()
            elif(self.state == "settingsmenu"):
                decision = await self.process.process()
                if(decision == -1):
                    pass
                elif(decision == 0):
                    self.process = self.get_screen_adjust_menu("Settings", "Screen Brightness", self.hardware.display.get_brightness(), self.hardware.display.set_brightness)
                    self.state = "slidermenu"
                elif(decision == 1):
                    self.process = self.get_screen_adjust_menu("Settings", "Volume", self.hardware.speaker.get_volume(), self.hardware.speaker.set_volume)
                    self.state = "slidermenu"
                elif(decision == 2):
                    self.process = self.get_screen_adjust_menu("Settings", "Button Brightness", self.hardware.blue_button.get_brightness(), self.set_button_brightness)
                    self.state = "slidermenu"
                elif(decision == 3):
                    self.process = self.get_main_menu()
                    self.state = "mainmenu"
            elif(self.state == "slidermenu"):
                decision = self.process.process()
                if(decision == -1):
                    pass
                elif(decision == 0):
                    self.process = self.get_settings_menu()
                    self.state = "settingsmenu"
                    self.hardware.all_LEDs_off()
            elif(self.state == "pausemenu"):
                #temp - pause menu not implemented, so send back to main menu.
                self.process = self.get_main_menu()
                self.state = "mainmenu"
            else:
                print("Unkown state: ")
                print(self.state)
                break
            
            # if(hardware.menu_button.is_pressed()):
            #     if(self.state == "pausemenu"):
            #         self.state = "playing"
            #     elif(self.state == "playing"):
            #         self.state = "pausemenu"
            #     while(hardware.menu_button.is_pressed()):
            #         time.sleep(.1)

            # Display battery info (should always be last in loop for "layering"
            if(not self.hardware.display.showing_battery):
                self.battery.show_battery()
                self.hardware.display.showing_battery = True
            #await asyncio.sleep(.01)


    def get_main_menu(self) -> menu.MainMenu:
        return menu.MainMenu("Main Menu", self.hardware, [SubMenuItem("Pong"), SubMenuItem("Snake"), SubMenuItem("Space Shooter"), SubMenuItem("Settings")])
    

    def get_settings_menu(self) -> menu.MainMenu:
        return menu.MainMenu("Settings", self.hardware, [SubMenuItem("Screen Brightness"), SubMenuItem("Volume"), SubMenuItem("Button Brightness"), SubMenuItem("Back")])
    

    def get_pause_menu(self) -> menu.MainMenu:
        return menu.MainMenu("PAUSED", self.hardware, [SubMenuItem("Screen Brightness"), SubMenuItem("Volume"), SubMenuItem("Button Brightness"), SubMenuItem("Restart"), SubMenuItem("Back")])
    

    def get_screen_adjust_menu(self, title, subtitle, initial_value, func) -> SliderMenu:
        return SliderMenu(title, subtitle, self.hardware, initial_value, func)
    

    def set_button_brightness(self, level):
        self.hardware.blue_button.set_brightness(level)
        self.hardware.green_button.set_brightness(level, False)
        self.hardware.white_button.set_brightness(level, False)
        self.hardware.red_button.set_brightness(level, False)