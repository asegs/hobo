import map
import random

DEMO = False
VEGETATION_GROWTH_RATE = 0.001
VEGETATION_ENCLOSED_BONUS = 10
VEGETATION_ENCLOSED_STANDARD = 6

undeveloped_levels = ["%", "&", "#"]

UNINITIALIZED = 'a'
WATER = ' '


def erode(mp, args):
    cycles = args.get('cycles', 5)
    tolerance = args.get('tolerance', 6)
    all_tiles = mp.iterate_coords()
    for i in range(0, cycles):
        for coord in all_tiles:
            borders = mp.count_borders(WATER, coord)
            if borders > tolerance:
                mp.grid[coord.row][coord.col] = WATER


def tile_uninitialized_and_by_water(mp, coord, water_percentage):
    return mp.tile_is(coord, UNINITIALIZED) and random.random() < water_percentage and mp.if_borders(WATER, coord, True)


def draw_streams(mp, args):
    initial_waters = args.get('initial_waters', 3)
    water_percentage = args.get('water_percentage', 0.5)
    traces = args.get('traces', 1)
    tiles = mp.width * mp.height
    for i in range(0, initial_waters):
        place = random.randint(0, tiles - 1)
        row = int(place / mp.width)
        col = place - row * mp.width
        mp.grid[row][col] = WATER

    all_tiles = mp.iterate_coords()
    for i in range(0, traces):
        for coord in all_tiles:
            if tile_uninitialized_and_by_water(mp, coord, water_percentage):
                mp.grid[coord.row][coord.col] = WATER
                if DEMO:
                    mp.display()
        for coord in all_tiles[::-1]:
            if tile_uninitialized_and_by_water(mp, coord, water_percentage):
                mp.grid[coord.row][coord.col] = WATER
                if DEMO:
                    mp.display()


def vegetation_thicken(mp, coord):
    value = mp.tile_at(coord)
    if value not in undeveloped_levels:
        return

    if value == '#':
        return

    surrounding_thick = mp.count_borders('#', coord)
    surrounding_medium = 0

    if value == '%':
        surrounding_medium = mp.count_borders('&', coord)

    enclosed_bonus = VEGETATION_ENCLOSED_BONUS if (
                                                              surrounding_thick + surrounding_thick) >= VEGETATION_ENCLOSED_STANDARD else 1

    surroundings_multiplier = (surrounding_thick * 3 + surrounding_medium) * enclosed_bonus
    if random.random() < VEGETATION_GROWTH_RATE * surroundings_multiplier:
        mp.tile_set(coord, undeveloped_levels[undeveloped_levels.index(value) + 1])


def draw_land(mp, args):
    ruggedness = args.get('ruggedness', 1) / 2
    cycles = args.get('land_cycles', 50)

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


m = map.Map(190, 54, UNINITIALIZED, [draw_streams, erode, draw_land], [vegetation_thicken])
map_args = {
    'spawns': 3,
    'spread': 0.5,
    'cycles': 10,
    'tolerance': 4,
    'ruggedness': 0.5,
    'land_cycles': 50

}
m.initialize_terrain(map_args)

m.display()
