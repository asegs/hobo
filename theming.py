import colorsys
import colorist

MAX_HUE = 138


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def full_rgb(text, fg, bg):
    return f"{colorist.BgColorRGB(bg[0], bg[1], bg[2]) }{colorist.ColorRGB(fg[0], fg[1], fg[2])}{text}{colorist.Color.OFF}{colorist.BgColor.OFF}"


def to_color_text(text, rgb):
    return f"{colorist.ColorRGB(rgb[0], rgb[1], rgb[2])}{text}{colorist.Color.OFF}"


def color_quality(worst, best, score):
    if score < min(worst, best) or score > max(worst, best):
        return hsv2rgb(0, 0.98, 0.64)
    slope = 1 / (best - worst)
    percent = slope * (score - worst)
    quality_score = (percent * MAX_HUE) / 360
    return hsv2rgb(quality_score, 0.98, 0.64)


def color_text_with_score(text, worst, best, score):
    return to_color_text(text, color_quality(worst, best, score))


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

DEEP_GREEN = (3, 84, 9)
MID_GREEN = (0, 156, 12)
LIGHT_GREEN = (95, 179, 46)

WATER = (45, 109, 194)
GREY = (142, 152, 153)
DARK_BROWN = (82, 48, 5)
TAN = (235, 134, 52)
