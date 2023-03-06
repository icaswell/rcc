from board import Board
from graphics import colorize


def parse_command(line):
  try:
    parts = line.strip().split()
    cmd = parts[0]
    args = []
    kwargs = dict()
    for part in parts[1:]:
        if part.startswith('--'):
            k, v = part[2:].split("=", 1)
            kwargs[k] = v
        elif part.startswith('-'):
            kwargs[part[1:]] = True
        else:
            args.append(part)
    return cmd, args, kwargs
  except:
    return None

def get_command():
  print("*=~"*27)
  # Loop to get a single command
  while True:
    line = input(colorize("enter command ('help' for help): ", 'green')).strip()
    cmd_parts = parse_command(line)
    if not cmd_parts:
      print(f"Parsing error for '{line}'. Please try again.")
      print_help()
      continue
    cmd, args, kwargs = cmd_parts 
    if cmd not in COMMAND_ACTIONS:
      print(f"unrecognized command '{line}'. Please try again.")
      print_help()
      continue
    else:
      return cmd, args, kwargs
 

COMMAND_ACTIONS = {"help", "q", "s", "m"}

def print_help():
    print(f"""
====================================
Here are some commands you can enter!
------------------------------------
    General format:
      $ command -option1 -option2 keyword_argument=
          {colorize('help', 'red')}: print this string.
          {colorize('s XY [-k]', 'red')}: select piece at square XY (alternate option -k: keep existing selection) 
          {colorize('m XY WZ', 'red')}: move the piece at square XY to square WZ
          {colorize('q', 'red')}: quit this game.

    """)


def main():
  board = Board(square_height=8, grid_width=8, border_width=1)
  while True:
    print("\n"*8)
    board.render()
    cmd, args, kwargs = get_command()
    if cmd == "q":
        break
    elif cmd == "m":
        start_square, end_square = args
        piece = board.get_pieces_on_square(start_square)[0]
        print(f"Selected {piece.name}")
        board.move_piece(piece, start_square, end_square)
    elif cmd == "s":
        assert len(args) ==  1 and len(args[0]) == 2
        square = board.square_from_a1_coordinates(args[0])
        continue_existing_selection = kwargs.get("k", False)
        board.select_square(square, continue_existing_selection=continue_existing_selection)
    elif cmd == "help":
        print_help()
    else:
        raise ValueError("Something is very wrong")


main()
