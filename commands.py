from graphics import colorize


def parse_command(line):
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
    if cmd not in COMMAND_ACTIONS:
      raise ValueError(f"unrecognized command '{line}'. Please try again.")
    return cmd, args, kwargs

def get_command():
    line = input(colorize("enter command ('help' for help): ", 'green')).strip()
 

# Augh this should somehow be decoubled from game.py
COMMAND_ACTIONS = {"h", "q", "s", "m", "v"}

def print_help():
    print(f"""
====================================
Here are some commands you can enter!
------------------------------------
    General format:
      $ command -option1 -option2 --keyword_argument=
          {colorize('h',      'red')}: print this string.
          {colorize('s XY [-k]', 'red')}: select piece at square XY (alternate option -k: keep existing selection) 
          {colorize('s -r',      'red')}: select a random piece) 
          {colorize('m XY',      'red')}: Move the selected piece to square XY
          {colorize('q',         'red')}: quit this game.
""")



