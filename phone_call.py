lines = {
    "count": [
        (6, "It's an open floor plan."),
        (9, "It's a standard layout."),
        (15, "There's a lot of rooms.")
    ],
    "room_size": [
        (40, "The rooms are tight."),
        (80, "The rooms are standard size."),
        (130, "The rooms are huge.")
    ],
    "door_max": [
        (1, "Each room only has one door."),
        (2, "Most rooms have two entry points."),
        (3, "We've got doors everywhere.")
    ],
    "smoke_chance": [
        (0.1, "We have terrible ventilation."),
        (0.2, "We left some fans on."),
        (0.3, "We've got a lot of windows open and forced air.")
    ],
    "fire_count": [
        (1, "I think we left the stove on."),
        (2, "We left a candle burning by the woodstove."),
        (3, "I think we had a bunch of little electrical fires.")
    ],
    "people": [
        (1, "My wife is home!"),
        (3, "A few people are home."),
        (5, "The whole family was sleeping.")
    ]
}


def get_line(value, key):
    options = lines[key]
    for (option_val, line) in options:
        if value <= option_val:
            return line + "  \n"
    return ""
