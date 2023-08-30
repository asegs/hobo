import theming
from dataclasses import dataclass


@dataclass
class Coord:
    row: int
    col: int


straight_borders = [
    Coord(0, -1),
    Coord(-1, 0),
    Coord(0, 1),
    Coord(1, 0)
]

diag_borders = [
    Coord(-1, -1),
    Coord(-1, 1),
    Coord(1, -1),
    Coord(1, 1)
]


def tile_to_color(tile):
    if tile == '#':
        return theming.to_rgb(' ', theming.DEEP_GREEN)
    elif tile == '&':
        return theming.to_rgb(' ', theming.MID_GREEN)
    elif tile == '%':
        return theming.to_rgb(' ', theming.LIGHT_GREEN)
    elif tile == ' ':
        return theming.to_rgb(' ', theming.WATER)
    else:
        return theming.to_rgb(' ', theming.GREY)


def coord_diff(c1: Coord, c2: Coord):
    return Coord(c1.row + c2.row, c1.col + c2.col)


class Map:
    def __init__(self, width, height, default, generators, tile_handlers):
        self.grid = [[default for i in range(width)] for j in range(height)]
        self.width = width
        self.height = height
        self.generators = generators
        self.tile_handlers = tile_handlers

    def coord_inbounds(self, coord: Coord):
        return 0 <= coord.row < self.height and 0 <= coord.col < self.width

    def iterate_coords(self):
        return [Coord(int(i / self.width), i % self.width) for i in range(self.height * self.width)]

    def tile_at(self, coord: Coord):
        if self.coord_inbounds(coord):
            return self.grid[coord.row][coord.col]
        return None

    def tile_set(self, coord: Coord, to: str):
        if self.coord_inbounds(coord):
            self.grid[coord.row][coord.col] = to

    def tile_is(self, coord: Coord, match: str):
        if self.coord_inbounds(coord):
            return self.tile_at(coord) == match
        return False

    def initialize_terrain(self, generator_args):
        for generator in self.generators:
            generator(self, generator_args)

    def simulate_turn(self):
        all_tiles = self.iterate_coords()
        for handler in self.tile_handlers:
            for coord in all_tiles:
                handler(self, coord)

    def display(self):
        for line in self.grid:
            for letter in line:
                print(tile_to_color(letter), end='')
            print()
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

    def cursor_to_top(self):
        print('\033[' + str(self.height) + 'A')
        print('\033[' + str(self.width) + 'D')