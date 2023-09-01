import sys

import input_handler
import theming
from dataclasses import dataclass


@dataclass
class Coord:
    row: int
    col: int


@dataclass
class Tile:
    fg: str
    bg: str


MOVEMENT_COORDS = {
    input_handler.Movement.UP: Coord(-1, 0),
    input_handler.Movement.RIGHT: Coord(0, 1),
    input_handler.Movement.DOWN: Coord(1, 0),
    input_handler.Movement.LEFT: Coord(0, -1),
}


straight_borders = [Coord(0, -1), Coord(-1, 0), Coord(0, 1), Coord(1, 0)]

diag_borders = [Coord(-1, -1), Coord(-1, 1), Coord(1, -1), Coord(1, 1)]


def coord_diff(c1: Coord, c2: Coord):
    return Coord(c1.row + c2.row, c1.col + c2.col)


class Map:
    def __init__(
        self,
        width: int,
        height: int,
        default_bg: str,
        default_fg: str,
        generators: list,
        tile_handlers: list,
        fg_theming: dict,
        bg_theming: dict,
        status_rules={},
    ):
        self.grid = [
            [Tile(default_fg, default_bg) for i in range(width)] for j in range(height)
        ]
        self.width = width
        self.height = height
        self.generators = generators
        self.tile_handlers = tile_handlers
        self.fg_theming = fg_theming
        self.bg_theming = bg_theming
        self.turns = 0
        self.status_rules = status_rules

    def coord_inbounds(self, coord: Coord):
        return 0 <= coord.row < self.height and 0 <= coord.col < self.width

    def iterate_coords(self):
        return [
            Coord(int(i / self.width), i % self.width)
            for i in range(self.height * self.width)
        ]

    def tile_at(self, coord: Coord):
        if self.coord_inbounds(coord):
            return self.grid[coord.row][coord.col]
        return None

    def tile_set(self, coord: Coord, to: str, fg=False):
        if self.coord_inbounds(coord):
            if fg:
                self.grid[coord.row][coord.col].fg = to
            else:
                self.grid[coord.row][coord.col].bg = to

    def tile_is(self, coord: Coord, match: str, fg=False):
        if self.coord_inbounds(coord):
            if fg:
                return self.tile_at(coord).fg == match
            else:
                return self.tile_at(coord).bg == match

        return False

    def initialize_terrain(self, generator_args):
        for generator in self.generators:
            generator(self, generator_args)

    def simulate_turn(self, turns):
        handlers_to_run = []
        for i in range(turns):
            self.turns += 1
            for handler_pair in self.tile_handlers:
                if self.turns % handler_pair[1] == 0:
                    handlers_to_run.append(handler_pair[0])
        all_tiles = self.iterate_coords()
        for handler in handlers_to_run:
            for coord in all_tiles:
                handler(self, coord)

    def display(self, stats={}):
        line_count = 0
        stat_keys = list(stats.keys())
        for line in self.grid:
            for tile in line:
                print(self.tile_to_color(tile), end="")
            if line_count < len(stat_keys):
                stat_name = stat_keys[line_count]
                print(stat_name + ": ", end="")
                if stat_name in self.status_rules:
                    rule = self.status_rules[stat_name]
                    print(
                        theming.color_text_with_score(
                            str(stats[stat_name]), rule[0], rule[1], stats[stat_name]
                        ),
                        end="   ",
                    )
                else:
                    print(
                        str(stats[stat_keys[line_count]]),
                        end="    ",
                    )

            print()
            line_count += 1
        if False:
            self.cursor_to_top()

    def if_borders(self, match, coord: Coord, diag=False):
        has_border = False
        if diag:
            for border in diag_borders:
                has_border |= self.tile_is(coord_diff(border, coord), match)
        for border in straight_borders:
            has_border |= self.tile_is(coord_diff(border, coord), match)

        return has_border

    def count_borders(self, match, coord, diag=True):
        count = 0
        if diag:
            for border in diag_borders:
                if self.tile_is(coord_diff(border, coord), match):
                    count += 1

        for border in straight_borders:
            if self.tile_is(coord_diff(border, coord), match):
                count += 1

        return count

    def tile_to_color(self, tile):
        bg_color = self.bg_theming.get(tile.bg, theming.GREY)
        fg_color = self.fg_theming.get(tile.fg, theming.GREY)
        return theming.full_rgb(tile.fg, fg_color, bg_color)

    def cursor_to_top(self):
        print("\033[" + str(self.height + 1) + "A", end="")
        print("\033[" + str(self.width) + "D", end="")
