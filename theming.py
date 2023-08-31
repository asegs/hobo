import colorsys

MAX_HUE = 138


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def to_rgb(text, rgb):
    return (
        "\033[48;2;"
        + str(rgb[0])
        + ";"
        + str(rgb[1])
        + ";"
        + str(rgb[2])
        + "m"
        + text
        + "\033[39m\033[49m"
    )


def to_color_text(text, rgb):
    return (
        "\033[38;2;"
        + str(rgb[0])
        + ";"
        + str(rgb[1])
        + ";"
        + str(rgb[2])
        + "m"
        + text
        + "\033[39m\033[49m"
    )


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

WATER = (33, 186, 207)
GREY = (142, 152, 153)
DARK_BROWN = (82, 48, 5)
