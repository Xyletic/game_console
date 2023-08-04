from xyletic_hardware import screen
import system_data.system_colors as colors

def draw_arrow(x: int, y: int, screen : screen.Screen, group=None):
    points = [(x, y+1), (x, y+5), (x+1, y+6), (x+3, y+6), (x+6, y+3), (x+3, y), (x+1, y)]
    return screen.draw_polygon(points, outline=colors.BLACK, close = False, colors=1, group=group)
    