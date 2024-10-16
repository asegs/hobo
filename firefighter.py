import random
import math
from dataclasses import dataclass
from core import input_handler, map, theming

map_height = 15
map_width = 50


def fresh_stats():
    return {
        "Vision": 1,
        "Weight": 1,
        "Breathing": 0,
        "Protection": 0,
        "Health": 100,
        "Breaths": 0,
        "Living": 0,
        "Direction": "",
        "Carrying": ""
    }


status_rules = {
    "Vision": (0, 5),
    "Weight": (10, 0),
    "Breathing": (0, 5),
    "Protection": (0, 5),
    "Health": (0, 100),
    "Breaths": (0, 5)
}

UNINITIALIZED = "a"


@dataclass
class Player:
    pos: map.Coord
    under: str
    stats: dict


grid = [[" " for i in range(map_width)] for j in range(map_height)]
visible = [["?" for i in range(map_width)] for j in range(map_height)]
smoke = {}
fire = {}
objects = {}
air = {}
tools = {}
saved = {}
equipped_gear = []
player_row = -1
player_col = -1
player_pos = " "
has_breaker = False
can_diffuse = False
can_extinguish = False
can_place_wall = False
can_place_cleaner = False
can_give_air = False
can_search = False
has_long = False
done = False
read_help = False
status = "Welcome."
breakers = ["Wrecker bar", "Heavy axe", "Long range wall wrecker"]
extinguishers = ["Light extinguisher", "Heavy extinguisher"]
ppl = ["A", "C", "B", "P"]

bg_themes = {
    "#": theming.DEEP_GREEN,
    "&": theming.MID_GREEN,
    "%": theming.LIGHT_GREEN,
    " ": theming.WATER,
    "a": theming.GREY,
    ".": theming.DARK_BROWN,
}


def print_grid():
    global grid
    for i in range(0, map_height):
        string = ""
        for j in range(0, map_width):
            string += grid[i][j]
        print(string)


def print_visible():
    global visible
    for i in range(0, map_height):
        string = ""
        for j in range(0, map_width):
            string += visible[i][j]
        if i == 0:
            string += " " + status
        if i == 1:
            string += " Health: " + str(health)
        if i == 2:
            string += " Carrying: " + carrying
        if i < len(equipped_gear) + 3 and i > 2:
            string += " Tool " + str(i - 2) + ".) " + equipped_gear[i - 3]
        if i == len(equipped_gear) + 3:
            word = ""
            for key in saved:
                word += " " + saved[key]
            string += " Saved: " + word
        if i == len(equipped_gear) + 4:
            string += " " + direction
        print(string)


def give_borders():
    global grid
    global visible
    for i in range(0, map_width):
        grid[0][i] = "#"
        grid[map_height - 1][i] = "#"
        visible[0][i] = "#"
        visible[map_height - 1][i] = "#"
    for i in range(1, map_height - 1):
        grid[i][0] = "#"
        grid[i][map_width - 1] = "#"
        visible[i][0] = "#"
        visible[i][map_width - 1] = "#"


def get_absolute_pos(row, col):
    return row * map_width + col


def get_coords_from_abs(absolute):
    row = int(absolute / map_width)
    col = absolute - row * map_width
    return [row, col]


def pick_random_coords():
    total = map_height * map_width
    num = random.randint(0, total - 1)
    return get_coords_from_abs(num)


def is_object(obj, row, col):
    try:
        if grid[row][col] == obj:
            return True
        else:
            return False
    except:
        return False


def if_borders(borders, row, col, diag=False):
    has_border = False
    if diag:
        has_border = is_object(borders, row - 1, col - 1) or is_object(borders, row + 1, col - 1) or is_object(borders,
                                                                                                               row - 1,
                                                                                                               col + 1) or is_object(
            borders, row + 1, col + 1)
    return has_border or is_object(borders, row - 1, col) or is_object(borders, row, col - 1) or is_object(borders, row,
                                                                                                           col + 1) or is_object(
        borders, row + 1, col)


def count_borders(obj, row, col, diag=True):
    count = 0
    for i in range(-1, 2):
        try:
            if grid[row - 1][col + i] == obj:
                count += 1
        except:
            count = count
        try:
            if grid[row + 1][col + i] == obj:
                count += 1
        except:
            count = count
    try:
        if grid[row][col - 1] == obj:
            count += 1
    except:
        count += 1
    try:
        if grid[row][col + 1] == obj:
            count += 1
    except:
        count += 1
    return count


def erode_smoke(tolerance=2):
    for row in range(0, map_height):
        for col in range(0, map_width):
            if grid[row][col] == "O":
                count = count_borders("O", row, col)
                count += count_borders("X", row, col)

                if count <= tolerance:
                    grid[row][col] = " "
                    try:
                        del smoke[get_absolute_pos(row, col)]
                    except:
                        pass


def draw_rooms_gen(mp: map.Map, args):
    count = args.get("count", 5)
    width_max = args.get("width_max", 12)
    width_min = args.get("width_min",6)
    height_max = args.get("height_max", 12)
    height_min = args.get("height_min",6)
    growth_percent = args.get("growth_percent", 0.9)
    door_max = args.get("door_max", 2)
    door_likelihood = args.get("door_likelihood", 0.08)

    # Draw outer border
    for x in range(0, map_width):
        m.tile_set(map.Coord(0, x), "#")
        m.tile_set(map.Coord(map_height - 1, x), "#")
    for y in range(0, map_height):
        m.tile_set(map.Coord(y, 0), "#")
        m.tile_set(map.Coord(y, map_width - 1), "#")

    for i in range(0, count):
        doors = 0
        coord = mp.random_coord()
        if mp.tile_at(coord).bg == "#":
            # Try again, already a wall!
            i -= 1
            continue
        mp.tile_set(coord, "#")
        x_max = 0
        for x in range(1, width_max + 1):
            if x < width_min or random.random() < growth_percent:
                offset_coord = map.Coord(coord.row, coord.col + x)
                if doors < door_max and random.random() < door_likelihood:
                    # Skip this add and place a door
                    # Won't guarantee any doors placed
                    doors += 1
                    pass
                x_max = x
                if mp.tile_is(offset_coord, "#"):
                    break
                mp.tile_set(offset_coord, "#")
            else:
                break
        y_max = 0
        for y in range(1, height_max + 1):
            if y < height_min or random.random() < growth_percent:
                offset_coord = map.Coord(coord.row + y, coord.col)
                if doors < door_max and random.random() < door_likelihood:
                    # Skip this add and place a door
                    # Won't guarantee any doors placed
                    doors += 1
                    pass
                y_max = y
                if mp.tile_is(offset_coord, "#"):
                    break
                mp.tile_set(offset_coord, "#")
            else:
                break
        for x in range(1, x_max + 1):
            mp.tile_set(map.Coord(coord.row + y_max, coord.col + x), "#")
        for y in range(1, y_max + 1):
            mp.tile_set(map.Coord(coord.row + y, coord.col + x_max), "#")


def make_border_arr(absolute, diag=True):
    coords = get_coords_from_abs(absolute)
    border = []
    full_borders = []
    b = [-1, 0, 0, -1, 0, 1, 1, 0]
    fb = [-1, -1, -1, 1, 1, -1, 1, 1]
    for i in range(0, 8, 2):
        try:
            if coords[0] + b[i] < 0 or coords[0] + b[i] >= map_height or coords[1] + b[i + 1] < 0 or coords[1] + b[
                i + 1] >= map_width:
                1 / 0
            grid[coords[0] + b[i]][coords[1] + b[i + 1]]
            border.append([coords[0] + b[i], coords[1] + b[i + 1]])
            full_borders.append([coords[0] + b[i], coords[1] + b[i + 1]])
        except:
            pass
    for i in range(0, 8, 2):
        try:
            if coords[0] + fb[i] < 0 or coords[0] + fb[i] >= map_height or coords[1] + fb[i + 1] < 0 or coords[1] + fb[
                i + 1] >= map_width:
                1 / 0
            grid[coords[0] + fb[i]][coords[1] + fb[i + 1]]
            full_borders.append([coords[0] + fb[i], coords[1] + fb[i + 1]])
        except:
            pass
    if diag:
        return full_borders
    else:
        return border


def get_all_within_distance(row, col, dist=3):
    valid = []
    counter = 0
    for i in range(0, map_height):
        for j in range(0, map_width):
            xdist = row - i
            ydist = col - j
            distance = math.sqrt(xdist ** 2 + ydist ** 2)
            if distance < dist:
                valid.append([i, j])
                counter += 1
    return valid


def get_all_type_within_distance(obj, row, col, dist=3):
    valid = []
    for i in range(0, map_height):
        for j in range(0, map_width):
            xdist = row - i
            ydist = col - j
            distance = math.sqrt(xdist ** 2 + ydist ** 2)
            if distance < dist and grid[i][j] == obj:
                valid.append([i, j])
    return valid


def explosion(row, col, fire_chance=0.25):
    global health
    global status
    valid = get_all_within_distance(row, col, 4)
    for pair in valid:
        print(pair[0])
        print(pair[1])
        if random.random() < fire_chance:
            if grid[pair[0]][pair[1]] == "G":
                status += " BOOM!"
                explosion(pair[0], pair[1])
            elif grid[pair[0]][pair[1]] == "@":
                health = int(health / 2)
            grid[pair[0]][pair[1]] = "X"
            in_flame += 1
            try:
                del objects[get_absolute_pos(pair[0], pair[1])]
                del air[get_absolute_pos(pair[0], pair[1])]
            except:
                pass


def spread_fire(fire_chance=0.2, smoke_chance=0.3):
    global fire
    to_add_fire = []
    to_add_smoke = []
    for absolute in fire:
        borders = make_border_arr(absolute)
        coords = get_coords_from_abs(absolute)
        for pair in borders:
            if random.random() < smoke_chance and grid[pair[0]][pair[1]] != "X" and grid[pair[0]][pair[1]] != "#":
                grid[pair[0]][pair[1]] = "O"
                smoke[get_absolute_pos(pair[0], pair[1])] = "O"
            if (random.random() < fire_chance and grid[pair[0]][pair[1]] != "#") or (random.random() < fire_chance / 2):
                try:
                    if objects[get_absolute_pos(pair[0], pair[1])] == "G":
                        status = "BOOM!"
                        explosion(pair[0], pair[1])
                        grid[pair[0]][pair[1]] = "X"
                except:
                    pass
                grid[pair[0]][pair[1]] = "X"
                to_add_fire.append(get_absolute_pos(pair[0], pair[1]))
    for absolute in smoke:
        borders = make_border_arr(absolute)
        coords = get_coords_from_abs(absolute)
        for pair in borders:
            if random.random() < smoke_chance and grid[pair[0]][pair[1]] != "X" and grid[pair[0]][pair[1]] != "#":
                grid[pair[0]][pair[1]] = "O"
                to_add_smoke.append(get_absolute_pos(pair[0], pair[1]))
    for absolute in to_add_fire:
        fire[absolute] = "X"
    for absolute in to_add_smoke:
        smoke[absolute] = "O"


def create_fire(count=1, cycles=10, fire_chance=0.03, smoke_chance=0.05):
    global grid
    for i in range(0, count):
        coords = pick_random_coords()
        if grid[coords[0]][coords[1]] == "X" or grid[coords[0]][coords[1]] == "x":
            i -= 1
            continue
        grid[coords[0]][coords[1]] = "X"
        fire[get_absolute_pos(coords[0], coords[1])] = "X"
        for i in range(0, cycles):
            spread_fire(fire_chance, smoke_chance)


def get_distance(absolute1, absolute2):
    coords1 = get_coords_from_abs(absolute1)
    coords2 = get_coords_from_abs(absolute2)
    x_dist = abs(coords1[1] - coords2[1])
    y_dist = abs(coords1[0] - coords2[0])
    return math.sqrt(x_dist ** 2 + y_dist ** 2)


def get_coords_away_from_fire(dist=5):
    while True:
        coords = pick_random_coords()
        full = get_absolute_pos(coords[0], coords[1])
        safe = True
        for absolute in fire:
            if get_distance(full, absolute) < dist or not (
                    grid[coords[0]][coords[1]] == " " or grid[coords[0]][coords[1]] == "O"):
                safe = False
        if safe:
            return coords


def populate(people=1, children=1, babies=1, animals=1, gas_tanks=3):
    global grid
    global player_row
    global player_col
    global player_pos
    global objects
    global air
    for i in range(0, people):
        coords = get_coords_away_from_fire()
        if grid[coords[0]][coords[1]] != "O":
            grid[coords[0]][coords[1]] = "A"
        objects[get_absolute_pos(coords[0], coords[1])] = "A"
        air[get_absolute_pos(coords[0], coords[1])] = 10
    for i in range(0, children):
        coords = get_coords_away_from_fire()
        if grid[coords[0]][coords[1]] != "O":
            grid[coords[0]][coords[1]] = "C"
        objects[get_absolute_pos(coords[0], coords[1])] = "C"
        air[get_absolute_pos(coords[0], coords[1])] = 7
    for i in range(0, babies):
        coords = get_coords_away_from_fire()
        if grid[coords[0]][coords[1]] != "O":
            grid[coords[0]][coords[1]] = "B"
        objects[get_absolute_pos(coords[0], coords[1])] = "B"
        air[get_absolute_pos(coords[0], coords[1])] = 5
    for i in range(0, animals):
        coords = get_coords_away_from_fire()
        if grid[coords[0]][coords[1]] != "O":
            grid[coords[0]][coords[1]] = "P"
        objects[get_absolute_pos(coords[0], coords[1])] = "P"
        air[get_absolute_pos(coords[0], coords[1])] = 7
    for i in range(0, gas_tanks):
        coords = get_coords_away_from_fire()
        if grid[coords[0]][coords[1]] != "O":
            grid[coords[0]][coords[1]] = "G"
        tools[get_absolute_pos(coords[0], coords[1])] = "G"
    coords = get_coords_away_from_fire()
    player_pos = grid[map_height - 1][coords[1]]
    grid[map_height - 1][coords[1]] = "@"
    player_row = map_height - 1
    player_col = coords[1]


def select_new(direction):
    global grid
    global player_row
    global player_col
    new_row = player_row
    new_col = player_col
    if direction == "a":
        new_row = player_row
        new_col = player_col - 1
    if direction == "w":
        new_row = player_row - 1
        new_col = player_col
    if direction == "s":
        new_row = player_row + 1
        new_col = player_col
    if direction == "d":
        new_row = player_row
        new_col = player_col + 1
    return [new_row, new_col]


def move_player(direction, distance=1):
    global player_row
    global player_col
    global grid
    global player_pos
    global done
    coords = select_new(direction)
    new_row = coords[0]
    new_col = coords[1]
    try:
        if new_col < 0 or new_row < 0 or new_row >= map_height or new_col >= map_width:
            finish = input("Leave house? (y/n):")
            if finish == "y":
                done = True
            return grid
        original_tile = player_pos
        new_pos = grid[new_row][new_col]
        if grid[new_row][new_col] == "#":
            return grid
        grid[player_row][player_col] = player_pos
        player_pos = grid[new_row][new_col]
        grid[new_row][new_col] = "@"
        player_row = new_row
        player_col = new_col
        return grid
    except:
        return grid


def get_xy_dist(row, col):
    global player_row
    global player_col
    return [col - player_col, player_row - row]


def get_angle_of_dist(xdist, ydist):
    return math.degrees(math.atan2(ydist, xdist))


def reveal_radial(width=30, stoppers=["#", "O", "X", "x"]):
    to_reveal = []
    global player_row
    global player_col
    global visible
    count = int(360 / width)
    buckets = [[] for i in range(count)]
    shortest_blocks = [10000 for i in range(count)]
    for row in range(0, map_height):
        for col in range(0, map_width):
            dist = get_xy_dist(row, col)
            angle = get_angle_of_dist(dist[0], dist[1])
            if dist[1] < 0:
                angle += 360
            value = grid[row][col]
            distance = math.sqrt(dist[0] ** 2 + dist[1] ** 2)
            buckets[(int(angle / width))].append([row, col, distance, value])
    block_counter = 0
    for bucket in buckets:
        shortest_block = 10000
        for row in bucket:
            if abs(row[2]) < shortest_block and row[3] in stoppers:
                shortest_block = abs(row[2])
        shortest_blocks[block_counter] = shortest_block
        block_counter += 1
    block_counter = 0
    for bucket in buckets:
        for i in range(0, len(bucket)):
            if bucket[i][2] <= shortest_blocks[block_counter]:
                to_reveal.append([bucket[i][0], bucket[i][1]])
    for piece in to_reveal:
        visible[piece[0]][piece[1]] = grid[piece[0]][piece[1]]


def smoke_vision(r=2):
    global player_row
    global player_col
    global visible
    for i in range(0, map_height):
        for j in range(0, map_width):
            dist = get_distance(get_absolute_pos(player_row, player_col), get_absolute_pos(i, j))
            if dist <= r:
                if dist == 0:
                    visible[i][j] = "@"
                elif get_absolute_pos(i, j) in objects:
                    visible[i][j] = objects[get_absolute_pos(i, j)]
                elif grid[i][j] == "O":
                    visible[i][j] = " "
                else:
                    visible[i][j] = grid[i][j]


def update_visible(smoke_vision=2):
    global visible
    global grid
    for row in range(0, map_height):
        for col in range(0, map_width):
            if visible[row][col] != "?" and visible[row][col] != "#":
                visible[row][col] = grid[row][col]


def is_numeric(string):
    try:
        int(string)
        return True
    except:
        return False


def select_loadout():
    global equipped_gear
    global breathing
    global protection
    global weight
    global vision
    global has_breaker
    global can_diffuse
    global can_extinguish
    global can_place_wall
    global can_place_cleaner
    global can_give_air
    global can_search
    global has_long
    gear = ["Wrecker bar, breaks walls, speed 1, weight 1", "Heavy axe, breaks walls speed 3, weight 2",
            "Audio enhancer, locates people, weight 2", "Light extinguisher, puts out fires, uses 3, weight 1",
            "Heavy extinguisher, puts out fires, uses 10, weight 5",
            "Smoke clearer, dissapates nearby smoke, uses 3, weight 1",
            "Gas diffuser, neutralizes gas pipes, uses 3, weight 1",
            "Oxygen tank, use on self or dying person, uses 2, weight 1",
            "Long range wall wrecker, break wall from a distance, uses 1, weight 3",
            "Temp wall, fill in a space to stop smoke,uses 3,weight 5"]
    print("You may have one head piece, one body piece, and several pieces of gear.")
    head = input(
        "For your head piece, would you like thermal goggles/mouthpiece (4 vision, 2 breathing, 1 weight 'g') or a rebreather (1 vision, 5 breathing, 3 weight 'r':")
    body = input(
        "For your body, would you like light gear (allows 5 gear, 1 protection, 1 weight 'l'), firefighter suit (allows 4 gear, 3 protection, 3 weight 'f'), or a heavy duty suit (allows 3 gear, 10 protection, 5 weight 'h':")
    if head == "g":
        equipped_gear.append("Thermal goggles")
        vision = 4
        breathing = 2
        weight = 1
    else:
        equipped_gear.append("Rebreather")
        vision = 1
        breathing = 5
        weight = 3
    if body == "l":
        equipped_gear.append("Light suit")
        gear_max = 5
        protection = 1
        weight += 1
    elif body == "f":
        equipped_gear.append("Firefighter suit")
        gear_max = 4
        protection = 3
        weight += 3
    else:
        equipped_gear.append("Heavy suit")
        gear_max = 3
        protection = 10
        weight += 5
    counter = 0
    while counter < gear_max:
        for b in range(0, len(gear)):
            print(str(b) + ".) " + gear[b])
        select = input("Choose an element from the list:")
        if is_numeric(select) and int(select) < len(gear) and int(select) >= 0:
            thing = (gear[int(select)].split(","))[0]
            equipped_gear.append(thing)
            if thing in breakers:
                has_breaker = True
                if thing == "Long range wall wrecker":
                    has_long = True
            elif thing == "Gas diffuser":
                can_diffuse = True
            elif thing in extinguishers:
                can_extinguish = True
            elif thing == "Temp wall":
                can_place_wall = True
            elif thing == "Smoke clearer":
                can_place_cleaner = True
            elif thing == "Oxygen tank":
                can_give_air = True
            elif thing == "Audio enhancer":
                can_search = True
            weight += int((gear[int(select)].split("weight "))[1])
            try:
                del gear[int(select)]
            except:
                pass
            counter += 1
        else:
            pass


def select_long(direction):
    global player_row
    global player_col
    coords = [player_row, player_col]
    mvmt = []
    if direction == "a":
        mvmt = [0, -1]
    elif direction == "w":
        mvmt = [-1, 0]
    elif direction == "s":
        mvmt = [1, 0]
    else:
        mvmt = [0, 1]
    while True:
        try:
            coords = [coords[0] + mvmt[0], coords[1] + mvmt[1]]
            orig_coords = coords
            if coords[0] < 0 or coords[1] < 0 or coords[1] >= map_width or coords[0] >= map_height:
                return orig_coords
            val = grid[coords[0]][coords[1]]
            if val == "#" or val in ppl or val == "G":
                return coords
        except:
            return select_new(direction)


def use_breaker():
    global grid
    global status
    global objects
    global air
    global visible
    if not has_breaker or carrying != "":
        return grid
    direction = input("Enter the direction of the wall to break:")
    coords = select_new(direction)
    if has_long:
        coords = select_long(direction)
    try:
        if grid[coords[0]][coords[1]] == "#":
            grid[coords[0]][coords[1]] = " "
            visible[coords[0]][coords[1]] = " "
            status = "Wall demolished."
    except:
        pass
    try:
        if objects[get_absolute_pos(coords[0], coords[1])] != "G":
            del objects[get_absolute_pos(coords[0], coords[1])]
            del air[get_absolute_pos(coords[0], coords[1])]
            grid[coords[0]][coords[1]] = " "
            visible[coords[0]][coords[1]] = " "
            status = "Bashed someone."
    except:
        pass
    try:
        if grid[coords[0]][coords[1]] == "G":
            explosion(coords[0], coords[1])
    except:
        pass
    return grid


def use_defuser():
    global grid
    global status
    global objects
    if not can_diffuse or carrying != "":
        return grid
    direction = input("Enter the direction of the gas to defuse:")
    coords = select_new(direction)
    try:
        if tools[get_absolute_pos(coords[0], coords[1])] == "G":
            grid[coords[0]][coords[1]] = " "
            del tools[get_absolute_pos(coords[0], coords[1])]
            status = "Gas defused."
            return grid
    except:
        return grid
    finally:
        return grid


def use_extinguisher():
    global grid
    global status
    global fire
    if not can_extinguish or carrying != "":
        return grid
    direction = input("Enter the direction of the fire to put out:")
    coords = select_new(direction)
    try:
        if grid[coords[0]][coords[1]] == "X":
            grid[coords[0]][coords[1]] = " "
            status = "Fire put out."
            del fire[get_absolute_pos(coords[0], coords[1])]
            return grid
    except:
        return grid
    finally:
        return grid


def use_temp_wall():
    global grid
    global status
    if not can_place_wall or carrying != "":
        return grid
    direction = input("Enter the direction of the wall to place:")
    coords = select_new(direction)
    try:
        if grid[coords[0]][coords[1]] == " " or grid[coords[0]][coords[1]] == "O":
            grid[coords[0]][coords[1]] = "#"
            status = "Wall placed."
            return grid
    except:
        return grid
    finally:
        return grid


def place_cleaner():
    global grid
    global status
    global tools
    if not can_place_cleaner or carrying != "":
        return grid
    direction = input("Enter the direction of the cleaner to place:")
    coords = select_new(direction)
    try:
        if grid[coords[0]][coords[1]] == " " or grid[coords[0]][coords[1]] == "O":
            grid[coords[0]][coords[1]] = "V"
            status = "Cleaner placed."
            tools[get_absolute_pos(coords[0], coords[1])] = "V"
            return grid
    except:
        return grid
    finally:
        return grid


def carry():
    global grid
    global status
    global objects
    global carrying
    global air
    direction = input("Enter the direction of the thing to pick up:")
    coords = select_new(direction)
    try:
        carrying = objects[get_absolute_pos(coords[0], coords[1])]
        status = "Picked up a " + carrying
        del objects[get_absolute_pos(coords[0], coords[1])]
        del air[get_absolute_pos(coords[0], coords[1])]
        grid[coords[0]][coords[1]] = " "
    except:
        pass
    return grid


def drop():
    global grid
    global status
    global objects
    global carrying
    if carrying == "":
        return grid
    direction = input("Enter the direction to drop them in:")
    coords = select_new(direction)
    try:
        if coords[0] < 0 or coords[1] < 0 or coords[0] >= map_height or coords[1] >= map_width:
            saved[len(saved)] = carrying
            status = "Saved " + carrying
            carrying = ""
            return grid
        if grid[coords[0]][coords[1]] == "X":
            status = "Threw " + carrying + " into the fire."
            carrying = ""
            return grid
        grid[coords[0]][coords[1]] = carrying
        objects[get_absolute_pos(coords[0], coords[1])] = carrying
        air[get_absolute_pos(coords[0], coords[1])] = 5
        status = "Put " + carrying + " down."
        carrying = ""
        return grid
    except:
        pass
    return grid


def give_air():
    global can_give_air
    global air
    global objects
    global breaths
    global health
    global grid
    global status
    if not can_give_air:
        return grid
    who = input("Do you want to use the air on yourself ('y') or someone else ('s')?:")
    if who == "s":
        direction = input("Enter the direction to give air in:")
        coords = select_new(direction)
        try:
            air[get_absolute_pos(coords[0], coords[1])] = 5
            status = "Gave " + objects[get_absolute_pos(coords[0], coords[1])] + " air."
            return grid
        except:
            pass
    else:
        breaths = breathing
        status = "Took some air."
        return grid


def clean():
    pairs = []
    for key in tools:
        if tools[key] == "V":
            coords = get_coords_from_abs(key)
            pairs.append([coords[0], coords[1]])
    for pair in pairs:
        valid = get_all_type_within_distance("O", pair[0], pair[1], 4)
        for two in valid:
            try:
                del smoke[get_absolute_pos(two[0], two[1])]
                grid[two[0]][two[1]] = " "
            except:
                pass


def get_nearest_npc():
    global objects
    global player_row
    global player_col
    shortest_dist = 10000
    closest = 0
    for key in objects:
        coords = get_coords_from_abs(key)
        xy = get_xy_dist(coords[0], coords[1])
        dist = math.sqrt(xy[0] ** 2 + xy[1] ** 2)
        if dist < shortest_dist:
            shortest_dist = dist
            closest = key
    return closest


def search():
    global can_search
    global grid
    global objects
    global direction
    if not can_search:
        return grid
    key = get_nearest_npc()
    coords = get_coords_from_abs(key)
    xy = get_xy_dist(coords[0], coords[1])
    if abs(xy[0]) > abs(xy[1]):
        if xy[0] < 0:
            direction = "<"
        else:
            direction = ">"
    else:
        if xy[1] < 0:
            direction = "v"
        else:
            direction = "^"
    return grid


def generate_scenario():
    global living
    phone_call = "Help!  My house is on fire!"
    rooms = random.randint(1, 14)
    room_size = random.randint(3, 15)
    origins = random.randint(1, 3)
    spread_mult = random.randint(1, 3)
    people = random.randint(0, 5)
    children = random.randint(0, 3)
    babies = random.randint(0, 3)
    pets = random.randint(0, 3)
    gas = random.randint(1, 5)
    time = random.randint(1, 30)
    living = people + children + babies + pets
    total = living + rooms + room_size + origins + spread_mult + gas + int(time / 6)
    give_borders()
    draw_rooms(rooms, room_size, room_size)
    create_fire(origins, time, 0.001 * spread_mult, 0.004)
    spread_fire()
    populate(people, children, babies, pets, gas)
    if rooms < 5:
        phone_call += "  It's a big open space."
    elif rooms < 8:
        phone_call += "  It's a normal house layout."
    else:
        phone_call += "  It's really cramped.  We have a lot of junk in there."
    if room_size < 6:
        phone_call += "  Be sure to check all our closets!"
    elif room_size < 10:
        phone_call += "  You should have space in the rooms."
    else:
        phone_call += "  The rooms are giant, be careful!"
    if origins == 1:
        phone_call += "  I think it's just one fire."
    elif origins < 4:
        phone_call += "  I left at least two candles burning."
    else:
        phone_call += "  It was during an indoor candlelight vigil."
    if spread_mult == 1:
        phone_call += "  Luckily, our house has flame retardant."
    else:
        phone_call += "  That house is bone dry.  Good luck."
    if people < 3:
        phone_call += "  There shouldn't be too many adults there."
    elif people < 5:
        phone_call += "  There will be as many as 4 adults."
    else:
        phone_call += "  We were having a house party."
    if children < 2:
        phone_call += "  My kids are home."
    else:
        phone_call += "  My kids also had some friends over."
    if babies < 2:
        phone_call += "  I don't think any babies were home."
    else:
        phone_call += "  My babies and our neighbors babies are in there!"
    if pets < 2:
        phone_call += "  I think our dog is in there!"
    else:
        phone_call += "  Please rescue all of my chonkers!"
    if gas < 3:
        phone_call += "  There shouldn't be too much gas stuff in there."
    else:
        phone_call += "  We run a lot of gas pipes, stay safe!"
    if time < 10:
        phone_call += "  It hasn't been on fire for that long."
    elif time < 20:
        phone_call += "  It's been on fire for 10 minutes already!"
    else:
        phone_call += "  I got home and could see the flames from the road!"
    phone_call += "[This house has a difficulty of " + str(int((total / 59) * 100)) + "%]"
    print(phone_call)


def survival():
    global health
    global breaths
    if player_pos != "O" and player_pos != "X":
        breaths = breathing
        if health < 100:
            health += 5
        if health > 100:
            health = 100
    if breaths <= 0:
        health -= 7
    if player_pos == "O":
        breaths -= 1
    if player_pos == "X":
        health -= (10 - protection)


def handler(inp):
    global grid
    global read_help
    if inp == "w" or inp == "a" or inp == "s" or inp == "d":
        move_player(inp)
        return grid
    elif inp == "b":
        return use_breaker()
    elif inp == "g":
        return use_defuser()
    elif inp == "e":
        return use_extinguisher()
    elif inp == "p":
        return use_temp_wall()
    elif inp == "c":
        return place_cleaner()
    elif inp == "f" and carrying == "":
        return carry()
    elif inp == "f" and carrying != "":
        return drop()
    elif inp == "h":
        read_help = False
        return grid
    elif inp == "t":
        return give_air()
    elif inp == "l":
        return search()
    else:
        return grid


def get_burnt():
    total = map_height * map_width
    count = 0
    for i in range(0, map_height):
        for j in range(0, map_width):
            if grid[i][j] == "X":
                count += 1
    return count / total


def score():
    global living
    global saved
    saved_percent = int((len(saved) / living) * 100)
    burnt_percent = int(get_burnt() * 100)
    print("Saved " + str(saved_percent) + "% of the living things.")
    print(str(burnt_percent) + "% of the house was burnt.")
    score = int(((100 - burnt_percent) + saved_percent) / 2)
    print("Your total score was " + str(score))


def people_die():
    to_delete = []
    global objects
    global grid
    global status
    for key in objects:
        coords = get_coords_from_abs(key)
        if grid[coords[0]][coords[1]] == "X":
            status = objects[key] + " burned to death."
            to_delete.append(key)
            del air[key]
        elif grid[coords[0]][coords[1]] == "O":
            air[key] -= 1
            if air[key] < -9:
                status = objects[key] + " suffocated."
                to_delete.append(key)
                del air[key]
            elif air[key] < 0:
                status = objects[key] + " is suffocating!"
                visible[coords[0]][coords[1]] = 10 + air[key]
        else:
            air[key] = 5
    for delete in to_delete:
        del objects[delete]


def fix():
    global grid
    global visible
    for i in range(0, map_height):
        for j in range(0, map_width):
            if grid[i][j] == "":
                grid[i][j] = " "
            if visible[i][j] == "":
                visible = " "


# give_borders()
# generate_scenario()
# reveal_radial()
# select_loadout()
# turns = 0
# while not done:
#     for i in range(0, 30):
#         print("")
#     for i in range(0, turns):
#         spread_fire(0.0003, 0.001)
#     erode_smoke()
#     clean()
#     reveal_radial()
#     update_visible()
#     smoke_vision()
#     survival()
#     if health < 0:
#         print("You died.")
#         break
#     people_die()
#     print_visible()
#     if not read_help:
#         print("WASD to move,E to extinguish,F to carry/drop,P to place wall,C to place cleaner,B to break wall")
#         read_help = True
#     move = input("Make your move:")
#     grid = handler(move)
#     turns = weight
#
# score()
m = map.Map(
    map_width,
    map_height,
    UNINITIALIZED,
    " ",
    [draw_rooms_gen],
    [],
    {},
    bg_themes,
    status_rules
)
m.initialize_terrain({})
m.display(fresh_stats())
