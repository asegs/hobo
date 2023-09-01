import map
import random
import theming
from dataclasses import dataclass
import input_handler

MAX_LOGS = 3


def fresh_stats(under):
    return {
        "Standing on": under,
        "Status": "Peachy",
        "Health": 10,
        "Food": 100,
        "Water": 100,
        "Turns awake": 0,
        "Logs": 0,
    }


@dataclass
class Player:
    pos: map.Coord
    under: str
    stats: dict


DEMO = False
VEGETATION_GROWTH_RATE = 0.001
VEGETATION_ENCLOSED_BONUS = 10
VEGETATION_ENCLOSED_STANDARD = 6

undeveloped_levels = ["%", "&", "#"]
costs = {"path": 1, "bridge": 3, "shelter": 3}

UNINITIALIZED = "a"
WATER = " "


def travel_time(letter):
    if letter in undeveloped_levels:
        return undeveloped_levels.index(letter) + 1
    return 0


def erode(mp: map.Map, args):
    cycles = args.get("cycles", 5)
    tolerance = args.get("tolerance", 6)
    all_tiles = mp.iterate_coords()
    for i in range(0, cycles):
        for coord in all_tiles:
            borders = mp.count_borders(WATER, coord)
            if borders > tolerance:
                mp.tile_set(coord, WATER)


def tile_uninitialized_and_by_water(mp, coord, water_percentage):
    return (
        mp.tile_is(coord, UNINITIALIZED)
        and random.random() < water_percentage
        and mp.if_borders(WATER, coord, True)
    )


def draw_streams(mp: map.Map, args):
    initial_waters = args.get("initial_waters", 3)
    water_percentage = args.get("water_percentage", 0.5)
    traces = args.get("traces", 1)
    tiles = mp.width * mp.height
    for i in range(0, initial_waters):
        place = random.randint(0, tiles - 1)
        row = int(place / mp.width)
        col = place - row * mp.width
        mp.grid[row][col].bg = WATER

    all_tiles = mp.iterate_coords()
    for i in range(0, traces):
        for coord in all_tiles:
            if tile_uninitialized_and_by_water(mp, coord, water_percentage):
                mp.tile_set(coord, WATER)
                if DEMO:
                    mp.display()
        for coord in all_tiles[::-1]:
            if tile_uninitialized_and_by_water(mp, coord, water_percentage):
                mp.tile_set(coord, WATER)
                if DEMO:
                    mp.display()


def vegetation_thicken(mp, coord):
    value = mp.tile_at(coord).bg
    if value not in undeveloped_levels:
        return

    if value == "#":
        return

    surrounding_thick = mp.count_borders("#", coord)
    surrounding_medium = 0

    if value == "%":
        surrounding_medium = mp.count_borders("&", coord)

    enclosed_bonus = (
        VEGETATION_ENCLOSED_BONUS
        if (surrounding_thick + surrounding_thick) >= VEGETATION_ENCLOSED_STANDARD
        else 1
    )

    surroundings_multiplier = (
        surrounding_thick * 3 + surrounding_medium
    ) * enclosed_bonus
    if random.random() < VEGETATION_GROWTH_RATE * surroundings_multiplier:
        mp.tile_set(coord, undeveloped_levels[undeveloped_levels.index(value) + 1])


def draw_land(mp, args):
    ruggedness = args.get("ruggedness", 1) / 2
    cycles = args.get("land_cycles", 50)

    all_tiles = mp.iterate_coords()

    for coord in all_tiles:
        land = random.random() / ruggedness
        if mp.tile_is(coord, UNINITIALIZED):
            if land < (1 / 3):
                mp.tile_set(coord, undeveloped_levels[2])
            elif land < (2 / 3):
                mp.tile_set(coord, undeveloped_levels[1])
            else:
                mp.tile_set(coord, undeveloped_levels[0])

    for i in range(cycles):
        for coord in all_tiles:
            vegetation_thicken(mp, coord)
        if DEMO:
            mp.display()


input_entry = input_handler.get_input_handler_with_movements()


def make_player(mp: map.Map) -> Player:
    row = random.randint(0, mp.height - 1)
    col = random.randint(0, mp.width - 1)

    coord = map.Coord(row, col)
    at = mp.tile_at(coord)
    if at.bg != " ":
        mp.tile_set(coord, "@", True)
        return Player(coord, " ", fresh_stats(at.fg))

    return make_player(mp)


def move_player(mp: map.Map, p: Player, move: input_handler.Movement):
    if move in map.MOVEMENT_COORDS:
        at_location = mp.tile_at(p.pos)
        new_coord = map.coord_diff(p.pos, map.MOVEMENT_COORDS[move])
        if mp.coord_inbounds(new_coord) and mp.tile_at(new_coord).bg != " ":
            if at_location.bg in undeveloped_levels[1:]:
                under_idx = undeveloped_levels.index(at_location.bg)
                mp.tile_set(p.pos, undeveloped_levels[under_idx - 1])

            mp.tile_set(p.pos, p.under, True)
            p.pos = new_coord
            p.under = mp.tile_at(new_coord).fg
            mp.tile_set(new_coord, "@", True)


def handle_player_stats(player, turn_length):
    player.stats["Turns awake"] += turn_length
    if turn_length > 1:
        player.stats["Logs"] = min(player.stats["Logs"] + 1, MAX_LOGS)

    if turn_length > 0:
        if player.stats["Water"] < 0:
            player.stats["Health"] -= 1

        if player.stats["Food"] < 0:
            player.stats["Health"] -= 1
        player.stats["Water"] -= turn_length * 2
        player.stats["Food"] -= turn_length


def build_handler(letter: str, handler: input_handler.InputHandler, prefix: str) -> str:
    return place_tile(m, player)


def interact_handler(
    letter: str, handler: input_handler.InputHandler, prefix: str
) -> str:
    return interact(m, player)


input_entry.register_handler("b", build_handler)
input_entry.register_handler("i", interact_handler)


def place_tile(mp: map.Map, p: Player):
    choice = input_entry.take_input(
        "Do you want to build a (p)ath, dig (w)ater, or build a (s)helter?"
    )
    if choice == "p":
        direction = input_entry.take_directional_input()
        if direction not in map.MOVEMENT_COORDS:
            return
        build_tile = map.coord_diff(p.pos, map.MOVEMENT_COORDS[direction])
        at_build = mp.tile_at(build_tile)
        cost = costs["bridge"] if at_build.bg == " " else costs["path"]
        if cost <= p.stats["Logs"]:
            mp.tile_set(build_tile, ".")
            p.stats["Logs"] -= cost
        else:
            p.stats["Status"] = "Need more logs"
    if choice == "w":
        direction = input_entry.take_directional_input()
        if direction not in map.MOVEMENT_COORDS:
            return
        water_position = map.coord_diff(p.pos, map.MOVEMENT_COORDS[direction])
        water_borders = mp.count_borders(WATER, water_position)
        if water_borders > 0:
            mp.tile_set(map.coord_diff(p.pos, map.MOVEMENT_COORDS[direction]), " ")
        else:
            p.stats["Status"] = "No water near"
    if choice == "s":
        direction = input_entry.take_directional_input()
        if direction not in map.MOVEMENT_COORDS:
            return
        build_tile = map.coord_diff(p.pos, map.MOVEMENT_COORDS[direction])
        at_build = mp.tile_at(build_tile)
        if at_build.bg == " ":
            p.stats["Status"] = "Too wet"
            return

        if costs["shelter"] > p.stats["Logs"]:
            p.stats["Status"] = "Need more logs"
            return

        mp.tile_set(build_tile, "^", True)
        p.stats["Logs"] -= costs["shelter"]


def interact(mp: map.Map, p: Player):
    direction = input_entry.take_directional_input()
    if direction not in map.MOVEMENT_COORDS:
        return
    build_tile = map.coord_diff(p.pos, map.MOVEMENT_COORDS[direction])
    at_build = mp.tile_at(build_tile)

    if at_build.bg == WATER:
        p.stats["Water"] = 100
        return

    if at_build.fg == "^":
        for i in range(p.stats["Health"], 10):
            mp.simulate_turn(10)
            p.stats["Health"] += 1


bg_themes = {
    "#": theming.DEEP_GREEN,
    "&": theming.MID_GREEN,
    "%": theming.LIGHT_GREEN,
    " ": theming.WATER,
    "a": theming.GREY,
    ".": theming.DARK_BROWN,
}

fg_themes = {"@": theming.RED, "^": theming.TAN}


status_rules = {
    "Food": (0, 100),
    "Water": (0, 100),
    "Health": (0, 10),
    "Turns awake": (500, 0),
    "Logs": (0, 3),
}

m = map.Map(
    165,
    54,
    UNINITIALIZED,
    " ",
    [draw_streams, erode, draw_land],
    [(vegetation_thicken, 20)],
    fg_themes,
    bg_themes,
    status_rules,
)
map_args = {
    "spawns": 3,
    "spread": 0.5,
    "cycles": 10,
    "tolerance": 4,
    "ruggedness": 0.5,
    "land_cycles": 50,
}
m.initialize_terrain(map_args)

player = make_player(m)

while True:
    m.cursor_to_top()
    m.display(player.stats)
    action = input_entry.take_input()
    if action in map.MOVEMENT_COORDS:
        move_player(m, player, action)
    turn_length = travel_time(m.tile_at(player.pos).bg)
    handle_player_stats(player, turn_length)
    m.simulate_turn(turn_length)
