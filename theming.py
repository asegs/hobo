def to_rgb(text, rgb):
    return '\033[48;2;' + str(rgb[0]) + ';' + str(rgb[1]) + ';' + str(rgb[2]) + 'm' + text + '\033[39m\033[49m'

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

DEEP_GREEN = (3, 84, 9)
MID_GREEN = (0, 156, 12)
LIGHT_GREEN = (95, 179, 46)

WATER = (33, 186, 207)
GREY = (142, 152, 153)

