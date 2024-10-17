from dataclasses import dataclass

from core import map

@dataclass
class Player:
    pos: map.Coord
    under: str
    stats: dict
    inventory: list
    selected: int


@dataclass
class Tool:
    name: str
    weight: int
    actions: dict
    stat_modifiers: dict


def break_wall(mp: map.Map, coord: map.Coord, turns: int):
    mp.simulate_turn(turns)
    mp.tile_set(coord, " ")


def light_break_wall(mp: map.Map, coord: map.Coord, player: Player):
    break_wall(mp, coord, 3)


def heavy_break_wall(mp: map.Map, coord: map.Coord, player: Player):
    break_wall(mp, coord, 1)


def put_out_fire(mp: map.Map, coord: map.Coord, turns: int):
    mp.simulate_turn(turns)
    mp.tile_set(coord, " ", True)


def light_put_out_fire(mp: map.Map, coord: map.Coord, player: Player):
    put_out_fire(mp, coord, 3)


def heavy_put_out_fire(mp: map.Map, coord: map.Coord, player: Player):
    put_out_fire(mp, coord, 1)

def place_cleaner(mp: map.Map, coord: map.Coord, player: Player):
    mp.simulate_turn(5)
    mp.tile_set(coord, "V", True)

def pick_up_person(mp: map.Map, coord: map.Coord, player: Player):
    mp.simulate_turn(3)
    mp.tile_set(coord, " ", True)
    player.stats["Carrying"] = "&"

def drop_person(mp: map.Map, coord: map.Coord, player: Player):
    if player.stats["Carrying"] == "":
        print("\nGood game, everybody is so happy now!")
        exit(0)
    mp.simulate_turn(5)
    player.stats["Carrying"] = ""

crowbar = Tool(
    "Crowbar",
    2,
    {
        "bg": {
            "#": light_break_wall
        },
        "fg": {

        }
    },
    {}
)

sledge = Tool(
    "Sledgehammer",
    5,
    {
        "bg": {
            "#": heavy_break_wall
        },
        "fg": {

        }
    },
    {}
)

light_extinguisher = Tool(
    "Small extinguisher",
    3,
    {
        "bg": {

        },
        "fg": {
            "X": light_put_out_fire
        }
    },
    {}
)

heavy_extinguisher = Tool(
    "Heavy extinguisher",
    5,
    {
        "bg": {

        },
        "fg": {
            "X": heavy_put_out_fire
        }
    },
    {}
)

cleaner = Tool(
    "Smoke filter",
    3,
    {
        "bg": {
            " ": place_cleaner
        },
        "fg": {

        }
    },
    {}
)

hands = Tool(
    "Gloves",
    0,
    {
        "bg": {
            "^": drop_person
        },
        "fg": {
            "&": pick_up_person
        }
    },
    {}
)
