import colorsys
import colorist

MAX_HUE = 138

BG_CACHE = {}
FG_CACHE = {}


def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def hex_to_ansi_string(hex_color):
    color_value = hex_to_rgb(hex_color)
    return (
        str(color_value[0])
        + ";"
        + str(color_value[1])
        + ";"
        + str(color_value[2])
        + "m"
    )


def cache_or_create(color, fg=True):
    global BG_CACHE
    global FG_CACHE
    if fg:
        if color in FG_CACHE:
            return FG_CACHE[color]
        color_string = "\033[38;2;" + hex_to_ansi_string(color)
        FG_CACHE[color] = color_string
        return color_string

    if color in BG_CACHE:
        return BG_CACHE[color]

    color_string = "\033[48;2;" + hex_to_ansi_string(color)
    FG_CACHE[color] = color_string
    return color_string


CLEAR_FG = "\033[39m"
CLEAR_BG = "\033[49m"


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def full_rgb(text, fg, bg, last_fg=None, last_bg=None, end_line=True):
    to_return = ""
    if fg != last_fg:
        to_return += cache_or_create(fg, True)
    if bg != last_bg:
        to_return += cache_or_create(bg, False)
    to_return += text
    if end_line:
        to_return += CLEAR_FG + CLEAR_BG

    return to_return


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


RED = "ff0000"
GREEN = "00ff00"
BLUE = "0000ff"

DEEP_GREEN = "035409"
MID_GREEN = "009c0c"
LIGHT_GREEN = "5fb32e"

WATER = "2d6dc2"
GREY = "8e9899"
DARK_BROWN = "523005"
TAN = "eb8634"

ATTENTION = "d4d419"
