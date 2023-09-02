from __future__ import annotations

import os
from typing import Callable
import click
import queue
from enum import Enum

TAB_CHAR = 9
ENTER_CHAR = 13
ESCAPE_CHAR = 27
SPACE_CHAR = 32
ESCAPE_BRACKET = 91

WINDOWS_ESCAPE_CHAR = 224

ESCAPE_TIMEOUT_SECONDS = 1


def empty_buffer_line():
    for i in range(0, 120):
        print(" ", end="")
    print("\r", end="")


def get_input_buffer(message: str):
    empty_buffer_line()
    click.echo(message, nl=False)
    return click.getchar()


def passthrough(letter: str, handler, prefix: str) -> str:
    return letter


def movement_passthrough(letter: str, handler, prefix: str) -> Movement:
    return MOVEMENT_MAP[ord(letter)]


class InputHandler:
    def __init__(self, default_handler=passthrough):
        self.input_queue = queue.Queue(0)
        self.input_registry = {}
        self.default_handler = default_handler

    def handle_letter(self, letter, prefix="") -> Movement | str:
        if letter in self.input_registry:
            return self.input_registry[letter](letter, self, prefix)
        return self.default_handler(letter, self, prefix)

    def take_input(self, prompt="") -> Movement | str:
        input_buffer = get_input_buffer(prompt)
        if prompt != "":
            # This isn't a top level event, this is in the context of a text prompt
            click.echo(input_buffer, nl=False)
            return input_buffer
        for letter in input_buffer:
            self.input_queue.put(letter)
        return self.handle_letter(self.input_queue.get())

    def take_directional_input(self):
        empty_buffer_line()
        click.echo("In which direction? ", nl=False)
        return self.take_input()

    def register_handler(
        self, letter: str, handler: Callable[[str, InputHandler, str], Movement | str]
    ):
        self.input_registry[letter] = handler


class Movement(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
    ENTER = 5
    ESCAPE = 6
    TAB = 7
    SPACE = 8


MOVEMENT_MAP = {
    65: Movement.UP,
    66: Movement.DOWN,
    67: Movement.RIGHT,
    68: Movement.LEFT,
    ENTER_CHAR: Movement.ENTER,
    ESCAPE_CHAR: Movement.ESCAPE,
    TAB_CHAR: Movement.TAB,
    SPACE_CHAR: Movement.SPACE,
    72: Movement.UP,
    75: Movement.LEFT,
    77: Movement.RIGHT,
    80: Movement.DOWN,
}


def escape_unix(letter: str, handler: InputHandler, prefix: str) -> Movement:
    try:
        next_letter = ord(handler.input_queue.get(True, ESCAPE_TIMEOUT_SECONDS))
    except queue.Empty:
        return Movement.ESCAPE

    if next_letter != ESCAPE_BRACKET:
        return Movement.ESCAPE

    try:
        movement_code = ord(handler.input_queue.get(True, ESCAPE_TIMEOUT_SECONDS))
    except queue.Empty:
        return Movement.ESCAPE

    if movement_code in MOVEMENT_MAP:
        return MOVEMENT_MAP[movement_code]

    return Movement.ESCAPE


def escape_windows(letter: str, handler: InputHandler, prefix: str) -> Movement:
    try:
        movement_code = ord(handler.input_queue.get(True, ESCAPE_TIMEOUT_SECONDS))
    except queue.Empty:
        return Movement.ESCAPE

    if movement_code in MOVEMENT_MAP:
        return MOVEMENT_MAP[movement_code]

    return Movement.ESCAPE


def get_input_handler_with_movements() -> InputHandler:
    handler = InputHandler()
    handler.register_handler(chr(ESCAPE_CHAR), escape_unix)
    handler.register_handler(chr(ENTER_CHAR), movement_passthrough)
    handler.register_handler(chr(TAB_CHAR), movement_passthrough)
    handler.register_handler(chr(SPACE_CHAR), movement_passthrough)
    handler.register_handler(chr(WINDOWS_ESCAPE_CHAR), escape_windows)
    return handler


if os.name == "nt":
    # this provides colored terminals on windows, for a good reason
    os.system("color")
