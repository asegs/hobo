from input_handler import InputHandler, get_input_handler_with_movements


def ask_for_number(letter: str, handler: InputHandler, prefix: str):
    return handler.take_input("Pick a number, 1, 2, or 3: ")


h = get_input_handler_with_movements()
h.register_handler("f", ask_for_number)
while True:
    print(h.take_input())
