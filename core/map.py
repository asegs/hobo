import math
import random

from core import input_handler
from core import theming
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


def coord_distance(coord1: Coord, coord2: Coord):
    x_dist = abs(coord1.col - coord2.col)
    y_dist = abs(coord1.row - coord2.row)
    return math.sqrt(x_dist**2 + y_dist**2)


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
        self.changes_since_display = []

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

            self.changes_since_display.append(coord)

    def tile_is(self, coord: Coord, match: str, fg=False, bypass_inbounds=False):
        if bypass_inbounds or self.coord_inbounds(coord):
            if fg:
                return self.tile_at(coord).fg == match
            else:
                return self.tile_at(coord).bg == match

        return False

    def random_coord(self):
        total_tiles = self.width * self.height
        place = random.randint(0, total_tiles - 1)
        row = int(place / self.width)
        col = place - row * self.width
        return Coord(row, col)

    def initialize_terrain(self, generator_args):
        for generator in self.generators:
            generator(self, generator_args)

    def simulate_turn(self, turns):
        handlers_to_run_on_tiles = []
        handlers_to_run_on_map = []
        for i in range(turns):
            self.turns += 1
            for handler, every, per_tile in self.tile_handlers:
                if self.turns % every == 0:
                    if per_tile:
                        handlers_to_run_on_tiles.append(handler)
                    else:
                        handlers_to_run_on_map.append(handler)

        for handler in handlers_to_run_on_map:
            handler(self)

        if len(handlers_to_run_on_tiles) > 0:
            all_tiles = self.iterate_coords()
            for handler in handlers_to_run_on_tiles:
                for coord in all_tiles:
                    handler(self, coord)

    def display(self, stats={}):
        self.changes_since_display = []
        line_count = 0
        stat_keys = list(stats.keys())
        for line in self.grid:
            last_bg = None
            last_fg = None
            pos = 0
            for tile in line:
                (to_print, last_fg, last_bg) = self.tile_to_color(
                    tile, last_fg, last_bg, (pos == self.width - 1)
                )
                pos += 1
                print(to_print, end="")
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

    def display_changes(self, stats={}):
        for change in self.changes_since_display:
            self.go_to(change)
            tile = self.tile_at(change)
            (to_print, last_fg, last_bg) = self.tile_to_color(tile, None, None, True)
            print(to_print, end="")

        stat_count = 0
        for stat_key in stats:
            self.go_to(Coord(stat_count, self.width))
            print(theming.CLEAR_BG, end="")
            print(theming.CLEAR_FG, end="")
            print(stat_key + ": ", end="")
            if stat_key in self.status_rules:
                rule = self.status_rules[stat_key]
                print(
                    theming.color_text_with_score(
                        str(stats[stat_key]), rule[0], rule[1], stats[stat_key]
                    ),
                    end="     ",
                )
            else:
                print(
                    str(stats[stat_key]),
                    end="      ",
                )
            stat_count += 1

        self.go_to(Coord(self.height - 1, self.width))
        print(theming.CLEAR_BG, end="")
        print(theming.CLEAR_FG, end="")
        self.changes_since_display = []

    def if_borders(self, match, coord: Coord, diag=False):
        not_edge = self.coord_not_edge(coord)
        has_border = False
        if diag:
            for border in diag_borders:
                has_border |= self.tile_is(
                    coord_diff(border, coord), match, bypass_inbounds=not_edge
                )
                if has_border:
                    return True
        for border in straight_borders:
            has_border |= self.tile_is(
                coord_diff(border, coord), match, bypass_inbounds=not_edge
            )
            if has_border:
                return True

        return has_border

    def count_borders(self, match, coord, diag=True):
        not_edge = self.coord_not_edge(coord)
        count = 0
        if diag:
            for border in diag_borders:
                if self.tile_is(
                        coord_diff(border, coord), match, bypass_inbounds=not_edge
                ):
                    count += 1

        for border in straight_borders:
            if self.tile_is(coord_diff(border, coord), match, bypass_inbounds=not_edge):
                count += 1

    def iterate_borders(self, coord: Coord, diag=True):
        borders = []
        count = 0
        if diag:
            for border in diag_borders:
                diag_coord = coord_diff(border, coord)
                if self.coord_inbounds(diag_coord):
                    borders.append(diag_coord)

        for border in straight_borders:
            straight_coord = coord_diff(border, coord)
            if self.coord_inbounds(straight_coord):
                borders.append(straight_coord)

        return borders

    def tile_to_color(self, tile, last_fg=None, last_bg=None, end_line=True):
        bg_color = self.bg_theming.get(tile.bg, theming.GREY)
        fg_color = self.fg_theming.get(tile.fg, theming.GREY)
        return (
            theming.full_rgb(tile.fg, fg_color, bg_color, last_fg, last_bg, end_line),
            fg_color,
            bg_color,
        )

    def cursor_to_top(self):
        print("\033[" + str(self.height + 1) + "A", end="")
        print("\033[" + str(999) + "D", end="")

    def go_to(self, coord):
        self.cursor_to_top()
        print("\033[" + str(coord.row) + "B", end="")
        print("\033[" + str(coord.col) + "C", end="")

    def coord_not_edge(self, coord: Coord) -> bool:
        return 0 < coord.row < self.height - 1 and 0 < coord.col < self.width - 1
