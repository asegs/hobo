import random
from core import input_handler, map, theming
from firefighter_arsenal import hands, crowbar, sledge, light_extinguisher, heavy_extinguisher, cleaner, Tool, Player
from phone_call import get_line

map_height = 15
map_width = 50
vacuum_range = 3

heal_out_of_combat = 1
fire_damage = 20

input_entry = input_handler.get_input_handler_with_movements()


def fresh_stats():
    return {
        "Vision": 1,
        "Weight": 1,
        "Breathing": 0,
        "Protection": 0,
        "Health": 100,
        "Breath": 10,
        "Living": 0,
        "Direction": "",
        "Carrying": "",
        "Equipped": "Gloves"
    }

status_rules = {
    "Vision": (0, 5),
    "Weight": (10, 0),
    "Breath": (-5, 10),
    "Protection": (0, 5),
    "Health": (0, 100),
    "Breaths": (0, 5)
}

UNINITIALIZED = "a"




flammability = {
    "bg": {
        "#": 0.2,
        " ": 0.1,
        "D": 0.15
    },
    "fg": {
        " ": 1.0,
        "@": 0.2,
        "O": 0.3
    }
}

bg_themes = {
    "#": theming.DEEP_GREEN,
    "a": theming.GREY,
    "D": theming.DARK_BROWN,
    " ": theming.GREY
}

fg_themes = {
    "X": theming.RED,
    "@": theming.ATTENTION,
    "O": theming.GREY,
    "V": theming.BLUE,
    "&": theming.DARK_BROWN
}


def get_random_direction_pair(mp: map.Map, coord: map.Coord):
    if coord.row == 0:
        row_dir = 1
    elif coord.row == mp.height - 1:
        row_dir = -1
    else:
        # Shorthand for -1 or 1
        row_dir = (round(random.random()) * 2) - 1

    if coord.col == 0:
        col_dir = 1
    elif coord.col == mp.width - 1:
        col_dir = -1
    else:
        col_dir = (round(random.random()) * 2) - 1

    return row_dir, col_dir


def take_action(tool: Tool, mp: map.Map, coord: map.Coord, p: Player):
    tile = mp.tile_at(coord)
    if tile.fg in tool.actions['fg']:
        tool.actions['fg'][tile.fg](mp, coord, p)
    if tile.bg in tool.actions['bg']:
        tool.actions['bg'][tile.bg](mp, coord, p)


def draw_real_rooms(mp: map.Map, args):
    count = args.get("count", 5)
    width_max = args.get("width_max", 12)
    width_min = args.get("width_min", 6)
    height_max = args.get("height_max", 12)
    height_min = args.get("height_min", 6)
    door_max = args.get("door_max", 2)
    door_likelihood = args.get("door_likelihood", 0.05)

    for i in range(0, count):
        coord = mp.random_coord()
        while not mp.tile_is(coord, "#"):
            coord = mp.random_coord()

        row_dir, col_dir = get_random_direction_pair(mp, coord)
        on_top = coord.row == 0 or coord.row == mp.height - 1
        x_size = random.randrange(width_min, width_max)
        y_size = random.randrange(height_min, height_max)
        doors_left = door_max

        if not on_top:
            for x in range(1, x_size + 1):
                new_coord = map.Coord(coord.row, coord.col + (col_dir * x))
                if mp.tile_is(new_coord, "#"):
                    x_size = x
                    break
                if doors_left > 0 and random.random() < door_likelihood:
                    doors_left -= 1
                    mp.tile_set(new_coord, "D")
                else:
                    mp.tile_set(new_coord, "#")

            offset = 1
            offset_coord = map.Coord(coord.row + (offset * row_dir), coord.col + (x_size * col_dir))
            while not mp.tile_is(offset_coord, "#"):
                if doors_left > 0 and random.random() < door_likelihood:
                    doors_left -= 1
                    mp.tile_set(offset_coord, "D")
                else:
                    mp.tile_set(offset_coord, "#")
                offset += 1
                offset_coord = map.Coord(coord.row + (offset * row_dir), coord.col + (x_size * col_dir))
        else:
            for y in range(1, y_size + 1):
                new_coord = map.Coord(coord.row + (row_dir * y), coord.col)
                if mp.tile_is(new_coord, "#"):
                    y_size = y
                    break
                if doors_left > 0 and random.random() < door_likelihood:
                    doors_left -= 1
                    mp.tile_set(new_coord, "D")
                else:
                    mp.tile_set(new_coord, "#")
            offset = 1
            offset_coord = map.Coord(coord.row + (y_size * row_dir), coord.col + (offset * col_dir))
            while not mp.tile_is(offset_coord, "#"):
                if doors_left > 0 and random.random() < door_likelihood:
                    doors_left -= 1
                    mp.tile_set(offset_coord, "D")
                else:
                    mp.tile_set(offset_coord, "#")
                offset += 1
                offset_coord = map.Coord(coord.row + (y_size * row_dir), coord.col + (offset * col_dir))


def draw_border(mp: map.Map, args):
    for x in range(0, map_width):
        m.tile_set(map.Coord(0, x), "#")
        m.tile_set(map.Coord(map_height - 1, x), "#")
    for y in range(0, map_height):
        m.tile_set(map.Coord(y, 0), "#")
        m.tile_set(map.Coord(y, map_width - 1), "#")


def fill_in_empty_space(mp: map.Map, _):
    for coord in mp.iterate_coords():
        if mp.tile_is(coord, "a"):
            mp.tile_set(coord, " ")


def add_people(mp: map.Map, args):
    count = args.get("people_count", 3)
    for i in range(0, count):
        while True:
            coord = mp.random_coord()
            tile = mp.tile_at(coord)
            if tile.bg == " " and tile.fg == " ":
                break
        mp.tile_set(coord, "&", True)


def gen_fire_spread(mp: map.Map, args):
    new_fire = []
    smoke_chance = args.get("smoke_chance", 0.3)
    fire = [coord for coord in mp.iterate_coords() if mp.tile_is(coord, "X", True)]
    for fire_coord in fire:
        borders = mp.iterate_borders(fire_coord)
        for border in borders:
            if random.random() < smoke_chance and mp.tile_is(border, " ") and not mp.tile_is(border, "X", True):
                mp.tile_set(border, "O", True)
            random_fire_chance = random.random()
            tile = mp.tile_at(border)
            tile_flammability = flammability["bg"].get(tile.bg, 0.5) * flammability["fg"].get(tile.fg, 0.5)
            if random_fire_chance < tile_flammability and not mp.tile_is(border, "X", True):
                mp.tile_set(border, "X", True)
                new_fire.append(border)
    # So we don't recursively grow the fire
    for f in new_fire:
        fire.append(f)


def health_manager(mp: map.Map, args):
    if player.under == "X":
        player.stats["Health"] -= fire_damage
    elif player.under == "O":
        player.stats["Breath"] -= 1
        if player.stats["Breath"] < 0:
            player.stats["Health"] -= player.stats["Breath"] ** 2
    else:
        player.stats["Breath"] = 10
        if player.stats["Health"] < 100:
            player.stats["Health"] += heal_out_of_combat

    if player.stats["Health"] < 0:
        die()



def gen_fire(mp: map.Map, args):
    count = args.get("fire_count", 1)
    for i in range(0, count):
        coord = mp.random_coord()
        mp.tile_set(coord, "X", True)


def vacuum_smoke(mp: map.Map, args):
    # TODO iterate closer tiles first
    smoke = [coord for coord in mp.iterate_coords() if mp.tile_is(coord, "O", True)]
    vacuums = [coord for coord in mp.iterate_coords() if mp.tile_is(coord, "V", True)]

    for vacuum_coord in vacuums:
        smoke_in_range = [coord for coord in smoke if map.coord_distance(coord, vacuum_coord) < vacuum_range]
        for coord in smoke_in_range:
            # Trace what was there last...I think we have this
            mp.tile_set(coord, " ", True)


def die():
    print("\n\nYou died.\n")
    exit(1)


def move_player(mp: map.Map, p: Player, move: input_handler.Movement):
    if move in map.MOVEMENT_COORDS:
        new_coord = map.coord_diff(p.pos, map.MOVEMENT_COORDS[move])
        if mp.tile_is(new_coord, "#"):
            return
        mp.tile_set(p.pos, p.under, True)
        p.pos = new_coord
        p.under = mp.tile_at(new_coord).fg
        mp.tile_set(new_coord, "@", True)



def configure():
    room_count = random.randrange(4, 12)
    min_width = random.randrange(4, 9)
    max_width = random.randrange(9, 15)
    min_height = random.randrange(3, 7)
    max_height = random.randrange(7, 12)
    door_max = random.randrange(1, 4)
    smoke_chance = random.randrange(5, 30) / 100
    fire_count = random.randrange(1, 4)
    people_count = random.randrange(1, 5)

    average_room_area = ((max_width + min_width) / 2) * ((max_height + min_height) / 2)
    circulation_quality = 0.3 - smoke_chance

    call = "Hi, our house is on fire!  \n"
    call += get_line(people_count, "people")
    call += get_line(room_count, "count")
    call += get_line(average_room_area, "room_size")
    call += get_line(door_max, "door_max")
    call += get_line(circulation_quality, "smoke_chance")
    call += get_line(fire_count, "fire_count")

    print(call)
    input_entry.take_input("Press any key to continue...")
    return {
        "count": room_count,
        "width_min": min_width,
        "width_max": max_width,
        "height_min": min_height,
        "height_max": max_height,
        "fire_count": fire_count,
        "door_max": door_max,
        "smoke_chance": smoke_chance,
        "people_count": people_count
    }


m = map.Map(
    map_width,
    map_height,
    UNINITIALIZED,
    " ",
    [draw_border, draw_real_rooms, gen_fire, gen_fire_spread, fill_in_empty_space, add_people],
    [
        (lambda mp: gen_fire_spread(mp, {}), 15, False),
        (lambda mp: vacuum_smoke(mp, {}), 20, False),
        (lambda mp: health_manager(mp, {}),1, False)
    ],
    fg_themes,
    bg_themes,
    status_rules
)
starting_pos = map.Coord(m.height - 1, round(m.width / 2))
player = Player(
    starting_pos,
    m.tile_at(starting_pos).fg,
    fresh_stats(),
    [
        hands,
        crowbar,
        sledge,
        light_extinguisher,
        heavy_extinguisher,
        cleaner
    ],
    0
)


m.initialize_terrain(configure())
m.tile_set(starting_pos, "@", True)
m.tile_set(starting_pos, "^")
m.display_changes(fresh_stats())

while True:
    action = input_entry.take_input()
    if action in map.MOVEMENT_COORDS:
        move_player(m, player, action)
    if action == 'e':
        direction = input_entry.take_directional_input()
        if direction not in map.MOVEMENT_COORDS:
            continue
        new_coord = map.coord_diff(player.pos, map.MOVEMENT_COORDS[direction])
        take_action(player.inventory[player.selected], m, new_coord, player)
    if (type(action) is not input_handler.Movement) and action.isnumeric():
        player.selected = int(action) - 1
        player.stats["Equipped"] = player.inventory[player.selected].name
    m.simulate_turn(1)
    for x in range(0, m.width):
        coord = map.Coord(m.height - 1, x)
        m.tile_set(coord, m.tile_at(coord).bg)
        m.tile_set(coord, m.tile_at(coord).fg, True)
    m.display_changes(player.stats)
