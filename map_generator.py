import click
import random


def ask_about_map():
    click.echo("Choose your map preset.")
    click.echo(
        "(d)efault, (i)slands, (f)orest, (m)eadow, (s)wamp, or (c)ustom: ", nl=False
    )
    choice = click.getchar()
    click.echo(choice, nl=False)
    settings = {}
    match choice:
        case "d":
            settings = {
                "spawns": 3,
                "spread": 0.5,
                "cycles": 1,
                "tolerance": 4,
                "ruggedness": 0.5,
                "land_cycles": 50,
                "berry_spawns": 50,
            }
        case "i":
            settings = {
                "spawns": 5,
                "spread": 0.55,
                "cycles": 1,
                "tolerance": 4,
                "ruggedness": 0.3,
                "land_cycles": 50,
                "berry_spawns": 50,
            }
        case "f":
            settings = {
                "spawns": 1,
                "spread": 0.35,
                "cycles": 3,
                "tolerance": 4,
                "ruggedness": 0.5,
                "land_cycles": 100,
                "berry_spawns": 50,
            }
        case "m":
            settings = {
                "spawns": random.randint(3, 5),
                "spread": 0.25,
                "cycles": 3,
                "tolerance": 4,
                "ruggedness": 0.1,
                "land_cycles": 20,
                "berry_spawns": 50,
            }

        case "s":
            settings = {
                "spawns": 12,
                "spread": 0.30,
                "cycles": 3,
                "tolerance": 4,
                "ruggedness": 0.3,
                "land_cycles": 65,
                "berry_spawns": 50,
            }
        case "c":
            settings = take_custom_input()
    print()
    if settings != {}:
        click.echo("Generating map...")
        return settings


def take_custom_input():
    print()
    settings = {
        "spawns": int(input("How many distinct bodies of water (0 - 20): ")),
        "spread": (
            int(input("With what percent rate of water spread (0 - 100): ")) / 100
        ),
        "cycles": int(input("For how many erosion cycles (0 - 5): ")),
        "tolerance": int(input("How jagged should coastlines be (3 - 8): ")),
        "ruggedness": (
            int(input("How densely forested should the terrain be (0 - 100): ")) / 100
        ),
        "land_cycles": int(input("How many plant growth cycles (0 - 150): ")),
        "berry_spawns": int(input("How much natural food abundance (0 - 100): ")),
    }

    return settings
